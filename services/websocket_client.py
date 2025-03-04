import logging
import json
from datetime import datetime
from typing import Dict, List, Callable, Any
from pybit.unified_trading import WebSocket
from config.settings import API_KEY, API_SECRET, TESTNET, WS_PRIVATE, SYMBOLS, CHANNELS

logger = logging.getLogger("bybit_collector.websocket")

class BybitWebSocketClient:
    def __init__(self, message_handler: Callable[[str, Dict[str, Any]], None]):
        self.message_handler = message_handler
        self.ws_public = None
        self.subscriptions = []
        
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
            
    def connect(self):
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
            
            self.ws_client = WebSocket(
                **ws_options,
                callback=self._handle_message
            )
            
            # Generate subscription topics
            self.subscriptions = self._generate_subscriptions()
            
            # Log subscriptions
            logger.info(f"Subscribing to: {self.subscriptions}")
            
            # Subscribe to topics
            self.ws_client.subscribe(self.subscriptions)
            
            logger.info("Successfully connected to Bybit WebSocket API")
            
        except Exception as e:
            logger.exception(f"Failed to connect to WebSocket: {e}")
            raise
            
    def disconnect(self):
        """Disconnect from WebSocket API."""
        if self.ws_client:
            try:
                self.ws_client.exit()
                logger.info("Disconnected from Bybit WebSocket API")
            except Exception as e:
                logger.error(f"Error disconnecting from WebSocket: {e}")