import asyncio
import logging
from datetime import datetime

from pybit.unified_trading import WebSocket

from config.settings import API_KEY, API_SECRET, SYMBOLS, TESTNET, TICKER_BATCH_SIZE
from services.data_processor import DataProcessor

logger = logging.getLogger("bybit_collector.websocket")


class BybitWebSocketClient:
    def __init__(self, data_processor: DataProcessor):
        self.ticker_data = {}
        self.ws_public = None
        self.ws_private = None
        self.subscriptions = []
        self.data_processor = data_processor
        # self.save_handler = save_handler

    def sync_handle_ticker(self, message):
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.handle_ticker(message))
        asyncio.run(self.handle_ticker(message))

    async def connect_public(self):
        """Connect to Bybit WebSocket API and subscribe to channels."""
        try:
            self.ws_public = WebSocket(
                testnet=False,
                channel_type='linear'
            )
            for symbol in SYMBOLS:  # Subscribe to all symbols
                self.ws_public.ticker_stream(symbol, self.sync_handle_ticker)
        except Exception as e:
            logger.exception(f"Failed to connect to WebSocket: {e}")
            raise

    async def handle_ticker(self, message):
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
                self.ticker_data[symbol].append(ticker_data)  # Append the copy
                
                # When the internal table reaches the configured batch size, 
                # queue for saving
                if len(self.ticker_data[symbol]) >= TICKER_BATCH_SIZE:
                    data_to_save = self.ticker_data[symbol].copy()
                    self.ticker_data[symbol] = []
                    print(f'save to database: {len(data_to_save)}')
                    logger.info(f'save to database: {len(data_to_save)}')
                    # self.save_handler(data_to_save)
                    await self.data_processor.save_to_database(data_to_save)
                
        except KeyError as e:
            print(f"KeyError in handle_ticker: {e}")

    async def connect_private(self):
        """Connect to Bybit WebSocket API and subscribe to channels."""
        try:
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
            
            # Subscribe to topics
            self.ws_private.subscribe(self.subscriptions)
            
            logger.info("Successfully connected to Bybit WebSocket API")
            
        except Exception as e:
            logger.exception(f"Failed to connect to WebSocket: {e}")
            raise
            
    async def disconnect(self):
        """Disconnect from WebSocket API and cleanup resources."""
        if self.ws_private:
            try:
                self.ws_private.exit()
                logger.info("Disconnected from Bybit WebSocket API")
            except Exception as e:
                logger.error(f"Error disconnecting from WebSocket: {e}")
        
        # Signal save thread to stop
        # await self.data_processor.stop()
