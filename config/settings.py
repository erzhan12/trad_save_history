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
SYMBOLS = os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT,LTCUSDT,SOLUSDT").split(",")
CHANNELS = os.getenv("CHANNELS", "orderbook.50,trade,kline.1m").split(",")

# Database Configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()  # Default to sqlite for testing
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "bybit_data")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Construct DATABASE_URL based on DB_TYPE
if DB_TYPE == "sqlite":
    DATABASE_URL = f"sqlite:///{DB_NAME}.db"
elif DB_TYPE == "postgresql":
    # Handle empty port for PostgreSQL
    port_suffix = f":{DB_PORT}" if DB_PORT else ""
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}{port_suffix}/{DB_NAME}"
elif DB_TYPE == "mysql":
    # Handle empty port for MySQL
    port_suffix = f":{DB_PORT}" if DB_PORT else ""
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}{port_suffix}/{DB_NAME}"
else:
    raise ValueError(f"Unsupported database type: {DB_TYPE}")

ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "t")

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "30"))
TICKER_BATCH_SIZE = int(os.getenv("TICKER_BATCH_SIZE", "100"))  # Number of ticker records to batch 
DB_SIZE_CHECK_INTERVAL = int(os.getenv("DB_SIZE_CHECK_INTERVAL", "30"))