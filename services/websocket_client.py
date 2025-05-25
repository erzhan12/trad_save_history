import logging
import json
from datetime import datetime
from typing import Dict, List, Callable, Any
from pybit.unified_trading import WebSocket
from config.settings import API_KEY, API_SECRET, TESTNET, WS_PRIVATE, SYMBOLS, CHANNELS
import time
from models.market_data import TickerData
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import get_db
import asyncio
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("bybit_collector.websocket")


class BybitWebSocketClient:
    def __init__(self, message_handler: Callable[[str, Dict[str, Any]], None]):
        self.ticker_data = []
        self.message_handler = message_handler
        self.ws_public = None
        self.ws_private = None
        self.subscriptions = []
        self.save_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.save_thread = None
        self._start_save_thread()
        
    def _start_save_thread(self):
        """Start the save thread."""
        self.save_thread = threading.Thread(target=self._save_worker, daemon=True)
        self.save_thread.start()

    def _save_worker(self):
        """Worker thread that processes save operations."""
        while True:
            data_to_save = self.save_queue.get()
            if data_to_save is None:  # Shutdown signal
                break
            try:
                self._save_to_database(data_to_save)
            except Exception as e:
                logger.error(f"Error in save thread: {e}")
            finally:
                self.save_queue.task_done()

    def _save_to_database(self, data_to_save):
        """Save ticker data to database synchronously."""
        try:
            with Session(get_db()) as session:
                ticker_objects = []
                for data in data_to_save:
                    ticker = TickerData(
                        symbol=data['symbol'],
                        tick_direction=data['tickDirection'],
                        price_24h_pcnt=float(data['price24hPcnt']),
                        last_price=float(data['lastPrice']),
                        prev_price_24h=float(data['prevPrice24h']),
                        high_price_24h=float(data['highPrice24h']),
                        low_price_24h=float(data['lowPrice24h']),
                        prev_price_1h=float(data['prevPrice1h']),
                        mark_price=float(data['markPrice']),
                        index_price=float(data['indexPrice']),
                        open_interest=float(data['openInterest']),
                        open_interest_value=float(data['openInterestValue']),
                        turnover_24h=float(data['turnover24h']),
                        volume_24h=float(data['volume24h']),
                        next_funding_time=int(data['nextFundingTime']),
                        funding_rate=float(data['fundingRate']),
                        bid1_price=float(data['bid1Price']),
                        bid1_size=float(data['bid1Size']),
                        ask1_price=float(data['ask1Price']),
                        ask1_size=float(data['ask1Size'])
                    )
                    ticker_objects.append(ticker)
                
                session.bulk_save_objects(ticker_objects)
                session.commit()
                
        except Exception as e:
            logger.error(f"Error saving ticker data: {e}")
            session.rollback()

    def _generate_subscriptions(self) -> List[str]:
        """Generate subscription topics based on configured symbols and channels."""
        subscriptions = []
        for symbol in SYMBOLS:
            for channel in CHANNELS:
                topic = f"{channel}.{symbol}"
                subscriptions.append(topic)
        return subscriptions
        
    def _handle_message(self, message: str):
        """Process incoming WebSocket messages."""
        try:
            data = json.loads(message)
            
            # Handle ping messages
            if "op" in data and data["op"] == "ping":
                logger.debug("Received ping, sending pong")
                return
                
            # Handle subscription confirmation
            if "op" in data and data["op"] == "subscribe":
                logger.info(f"Successfully subscribed to: {data.get('args', [])}")
                return
                
            # Handle errors
            if "success" in data and not data["success"]:
                logger.error(f"Error from WebSocket: {data}")
                return
                
            # Handle actual data messages
            if "topic" in data and "data" in data:
                topic = data["topic"]
                topic_parts = topic.split(".")
                
                # Determine channel type (orderbook, trade, kline)
                channel_type = topic_parts[0]
                
                # Pass to message handler
                self.message_handler(channel_type, data)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode WebSocket message: {message}")
        except Exception as e:
            logger.exception(f"Error processing WebSocket message: {e}")
            
    def connect_public(self):
        """Connect to Bybit WebSocket API and subscribe to channels."""
        try:
            self.ws_public = WebSocket(
                testnet=False,
                channel_type='linear'
            )
            self.ws_public.ticker_stream('BTCUSDT', self.handle_ticker)
        except Exception as e:
            logger.exception(f"Failed to connect to WebSocket: {e}")
            raise

    def handle_ticker(self, message):
        try:
            ticker_data = message['data']
            print(f'handle ticker Last Price: {ticker_data["lastPrice"]} {ticker_data["turnover24h"]}')
            
            # If this is the first entry, append it
            if not self.ticker_data:
                self.ticker_data.append(ticker_data)
                return

            # Get the last entry
            last_data = self.ticker_data[-1]
            
            # Compare all fields except timestamp-related ones
            fields_to_compare = [
                'symbol', 'tickDirection', 'price24hPcnt', 'lastPrice',
                'prevPrice24h', 'highPrice24h', 'lowPrice24h', 'prevPrice1h',
                'markPrice', 'indexPrice', 'openInterest', 'openInterestValue',
                'turnover24h', 'volume24h', 'nextFundingTime', 'fundingRate',
                'bid1Price', 'bid1Size', 'ask1Price', 'ask1Size'
            ]
            
            # Check if any field has changed
            has_changes = any(
                ticker_data[field] != last_data[field]
                for field in fields_to_compare
            )
            
            # Only append if there are changes
            if has_changes:
                self.ticker_data.append(ticker_data)
                
                # When the internal table has 1000 rows, queue for saving
                if len(self.ticker_data) >= 1000:
                    # Create a copy of current data
                    data_to_save = self.ticker_data.copy()
                    self.ticker_data = []  # Clear immediately
                    
                    # Queue the save operation
                    self.save_queue.put(data_to_save)
                
        except KeyError:
            pass

    def connect_private(self):
        """Connect to Bybit WebSocket API and subscribe to channels."""
        try:
            # Initialize WebSocket client
            ws_url = "wss://stream-testnet.bybit.com/v5" if TESTNET else "wss://stream.bybit.com/v5"
            
            ws_options = {
                "api_key": API_KEY,
                "api_secret": API_SECRET,
                # "channel_type": "private" if WS_PRIVATE else "public",
                "channel_type": "linear",
                "test": TESTNET,
                "logging_level": logging.DEBUG,
            }
            
            self.ws_private = WebSocket(
                **ws_options,
                callback=self._handle_message
            )
            
            # Generate subscription topics
            self.subscriptions = self._generate_subscriptions()
            
            # Log subscriptions
            logger.info(f"Subscribing to: {self.subscriptions}")
            
            # Subscribe to topics
            self.ws_private.subscribe(self.subscriptions)
            
            logger.info("Successfully connected to Bybit WebSocket API")
            
        except Exception as e:
            logger.exception(f"Failed to connect to WebSocket: {e}")
            raise
            
    def disconnect(self):
        """Disconnect from WebSocket API and cleanup threads."""
        if self.ws_private:
            try:
                self.ws_private.exit()
                logger.info("Disconnected from Bybit WebSocket API")
            except Exception as e:
                logger.error(f"Error disconnecting from WebSocket: {e}")
        
        # Signal save thread to stop
        self.save_queue.put(None)
        if self.save_thread:
            self.save_thread.join()
        self.executor.shutdown(wait=True)