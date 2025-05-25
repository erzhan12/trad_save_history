import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.market_data import Orderbook, Trade, Kline, TickerData
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("bybit_collector.processor")


class DataProcessor:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def process_message(self, channel_type: str, message: Dict[str, Any]):
        """Process and save WebSocket message data based on channel type."""
        try:
            if channel_type.startswith("orderbook"):
                self._process_orderbook(message)
            elif channel_type == "trade":
                self._process_trade(message)
            elif channel_type.startswith("kline"):
                self._process_kline(message)
            else:
                logger.warning(f"Unknown channel type: {channel_type}")
        except Exception as e:
            logger.exception(f"Error processing {channel_type} data: {e}")

    def _process_orderbook(self, message: Dict[str, Any]):
        """Process orderbook data."""
        try:
            topic = message["topic"]
            symbol = topic.split(".")[-1]
            data = message["data"]

            # Create orderbook entry
            orderbook = Orderbook(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(data["ts"] / 1000),
                asks=data["a"],
                bids=data["b"]
            )

            # Save to database
            self.db_session.add(orderbook)
            self.db_session.commit()

            logger.debug(f"Saved orderbook for {symbol}")
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error saving orderbook data: {e}")

    def _process_trade(self, message: Dict[str, Any]):
        """Process trade data."""
        try:
            topic = message["topic"]
            symbol = topic.split(".")[-1]
            trades_data = message["data"]

            for trade_data in trades_data:
                # Check if trade already exists
                existing_trade = self.db_session.query(Trade).filter_by(trade_id=trade_data["i"]).first()
                if existing_trade:
                    continue

                # Create trade entry
                trade = Trade(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(int(trade_data["T"]) / 1000),
                    trade_id=trade_data["i"],
                    price=float(trade_data["p"]),
                    size=float(trade_data["v"]),
                    side=trade_data["S"]
                )

                # Save to database
                self.db_session.add(trade)

            self.db_session.commit()
            logger.debug(f"Saved {len(trades_data)} trades for {symbol}")
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error saving trade data: {e}")

    def _process_kline(self, message: Dict[str, Any]):
        """Process kline (candle) data."""
        try:
            topic = message["topic"]
            topic_parts = topic.split(".")
            interval = topic_parts[1]
            symbol = topic_parts[2]
            klines_data = message["data"]

            for kline_data in klines_data:
                # Convert timestamp to datetime
                start_time = datetime.fromtimestamp(int(kline_data["start"]) / 1000)

                # Check if kline already exists
                existing_kline = self.db_session.query(Kline).filter_by(
                    symbol=symbol,
                    interval=interval,
                    start_time=start_time
                ).first()

                # Update or create kline
                if existing_kline:
                    existing_kline.open_price = float(kline_data["open"])
                    existing_kline.high_price = float(kline_data["high"])
                    existing_kline.low_price = float(kline_data["low"])
                    existing_kline.close_price = float(kline_data["close"])
                    existing_kline.volume = float(kline_data["volume"])
                else:
                    kline = Kline(
                        symbol=symbol,
                        interval=interval,
                        start_time=start_time,
                        open_price=float(kline_data["open"]),
                        high_price=float(kline_data["high"]),
                        low_price=float(kline_data["low"]),
                        close_price=float(kline_data["close"]),
                        volume=float(kline_data["volume"])
                    )
                    self.db_session.add(kline)

            self.db_session.commit()
            logger.debug(f"Saved {len(klines_data)} klines for {symbol}")
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error saving kline data: {e}")

    def _process_ticker(self, ticker_data: Dict[str, Any]):
        """Process ticker data."""
        try:
            # Parse ticker data and append it to local memory and at some period of time save it to the database asynchronously
            self.ticker_data.append(ticker_data)
            if len(self.ticker_data) > 100:
                self.save_ticker_data()
        except Exception as e:
            logger.exception(f"Error saving ticker data: {e}")

    def save_ticker_data(self):
        """Save ticker data to the database."""
        try:
            # Save ticker data to the database
            self.db_session.bulk_insert_mappings(TickerData, self.ticker_data)
            self.db_session.commit()
            self.ticker_data = []
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error saving ticker data: {e}")
