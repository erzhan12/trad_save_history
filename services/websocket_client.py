import logging
from datetime import datetime
from typing import Any, Dict

from pybit.unified_trading import WebSocket

from config.settings import API_KEY, API_SECRET, SYMBOLS, TESTNET, TICKER_BATCH_SIZE
from services.data_processor import DataProcessor

logger = logging.getLogger("bybit_collector.websocket")


class BybitWebSocketClient:
    def __init__(self):
        self.ticker_data: Dict[str, list[Dict[str, Any]]] = {}
        self.ws_public = None
        self.ws_private = None
        self.subscriptions: list[str] = []
        self.data_processor = DataProcessor()

    def connect_public(self):
        """Connect to Bybit WebSocket API and subscribe to channels."""
        try:
            self.ws_public = WebSocket(
                testnet=TESTNET,
                channel_type="linear",
            )
            for symbol in SYMBOLS:  # Subscribe to all symbols
                self.ws_public.ticker_stream(symbol, self.handle_ticker)
        except Exception as e:
            logger.exception(f"Failed to connect to WebSocket: {e}")
            raise

    def handle_ticker(self, message):
        try:
            ticker_data = message['data'].copy()  # Create a copy of incoming data
            ticker_data['timestamp'] = datetime.now()
            symbol = ticker_data['symbol']
            
            # If this is the first entry, append it
            if not self.ticker_data.get(symbol):
                self.ticker_data[symbol] = []
                self.ticker_data[symbol].append(ticker_data)
                return

            # Get the last entry for the symbol
            last_data = self.ticker_data[symbol][-1]
            # Compare all fields except timestamp-related ones
            fields_to_compare = [
                # 'symbol', 'tickDirection', 'price24hPcnt', 
                'lastPrice',
                # 'prevPrice24h', 'highPrice24h', 'lowPrice24h', 'prevPrice1h',
                # 'markPrice', 'indexPrice', 'openInterest', 
                # 'openInterestValue',
                # 'turnover24h', 'volume24h', 'nextFundingTime', 'fundingRate',
                # 'bid1Price', 'bid1Size', 'ask1Price', 'ask1Size'
            ]
            
            # Check if any field has changed
            has_changes = any(
                ticker_data[field] != last_data[field]
                for field in fields_to_compare
            )
            
            # Only append if there are changes
            if has_changes:
                # print(f'has changes: {ticker_data["lastPrice"]}')
                self.ticker_data[symbol].append(ticker_data)  # Append the copy
                
                # When the internal table reaches the configured batch size, 
                # queue for saving
                if len(self.ticker_data[symbol]) >= TICKER_BATCH_SIZE:
                    data_to_save = self.ticker_data[symbol].copy()
                    self.ticker_data[symbol] = []
                    # print(f'save to database: {len(data_to_save)}')
                    logger.info(f'save to database: {len(data_to_save)}')
                    self.data_processor.add_to_save_queue(data_to_save) 
                
        except KeyError as e:
            print(f"KeyError in handle_ticker: {e}")

    def connect_private(self):
        """Connect to Bybit WebSocket API and subscribe to channels."""
        try:
            # Initialize WebSocket client
            # ws_url = "wss://stream-testnet.bybit.com/v5" if TESTNET else "wss://stream.bybit.com/v5"
            
            ws_options = {
                "api_key": API_KEY,
                "api_secret": API_SECRET,
                "channel_type": "linear",
                "test": TESTNET,
                "logging_level": logging.DEBUG,
            }
            
            self.ws_private = WebSocket(
                **ws_options,
                callback=self._handle_message
            )
            
            # Generate subscription topics
            # self.subscriptions = self._generate_subscriptions()
            
            # Log subscriptions
            # logger.info(f"Subscribing to: {self.subscriptions}")
            
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
        self.data_processor.stop()
