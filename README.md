# File: README.md
# Bybit Data Collector

A Python application that collects real-time market data from Bybit's WebSocket API and stores it in a SQLite database using SQLAlchemy.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=erzhan12_trad_save_history&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=erzhan12_trad_save_history)

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=erzhan12_trad_save_history)](https://sonarcloud.io/summary/new_code?id=erzhan12_trad_save_history)

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=erzhan12_trad_save_history)
## Features

- Connects to Bybit WebSocket API using pybit.unified_trading
- Supports multiple symbols and data channels (orderbook, trades, klines)
- Stores data in SQLite database with SQLAlchemy ORM
- Configurable via environment variables
- Proper logging and error handling

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update the configuration
4. Initialize the database:
   ```
   python main.py
   ```

## Configuration

Configure the application using environment variables or by editing the `.env` file:

- `BYBIT_API_KEY`: Your Bybit API key
- `BYBIT_API_SECRET`: Your Bybit API secret
- `USE_TESTNET`: Set to "True" to use Bybit's testnet
- `WS_PRIVATE`: Set to "True" to use private WebSocket streams (requires API credentials)
- `SYMBOLS`: Comma-separated list of symbols to subscribe to (e.g., "BTCUSDT,ETHUSDT")
- `CHANNELS`: Comma-separated list of channels (e.g., "orderbook.50,trade,kline.1m")
- `DATABASE_URL`: SQLAlchemy database URL
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `DATA_RETENTION_DAYS`: Number of days to retain data (for future cleanup jobs)
- `TICKER_BATCH_SIZE`: Number of ticker records to batch before saving to database

## Usage

Start the application:

```
python main.py
```

The application will:
1. Connect to Bybit's WebSocket API
2. Subscribe to the specified channels and symbols
3. Process incoming data and store it in the database
4. Run continuously until interrupted (Ctrl+C)

## Database Schema

- **Orderbooks**: Stores orderbook snapshots
- **Trades**: Stores individual trades
- **Klines**: Stores candle/kline data

## License

MIT

# File: .env.example
# Bybit API Configuration
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
USE_TESTNET=True

# WebSocket Configuration
WS_PRIVATE=False
SYMBOLS=BTCUSDT,ETHUSDT
CHANNELS=orderbook.50,trade,kline.1m

# Database Configuration
DATABASE_URL=sqlite:///bybit_data.db
ECHO_SQL=False

# Application Configuration
LOG_LEVEL=INFO
DATA_RETENTION_DAYS=30
TICKER_BATCH_SIZE=1000  # Number of ticker records to batch before saving to database