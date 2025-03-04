import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_KEY = os.getenv("BYBIT_API_KEY", "")
API_SECRET = os.getenv("BYBIT_API_SECRET", "")
TESTNET = os.getenv("USE_TESTNET", "False").lower() in ("true", "1", "t")

# WebSocket Configuration
WS_PRIVATE = os.getenv("WS_PRIVATE", "False").lower() in ("true", "1", "t")
SYMBOLS = os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT").split(",")
CHANNELS = os.getenv("CHANNELS", "orderbook.50,trade,kline.1m").split(",")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bybit_data.db")
ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "t")

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "30"))