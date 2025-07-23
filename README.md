# Bybit Data Collector

A Python application that collects real-time market data from Bybit's WebSocket API and stores it in a database using SQLAlchemy. The application supports multiple database backends (SQLite, PostgreSQL, MySQL) and provides comprehensive data collection for trading analysis.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=erzhan12_trad_save_history&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=erzhan12_trad_save_history)

## Features

- **Real-time Data Collection**: Connects to Bybit WebSocket API using pybit.unified_trading
- **Multi-Symbol Support**: Subscribe to multiple trading pairs simultaneously
- **Multiple Data Channels**: Collect orderbook, trades, and kline data
- **Flexible Database Support**: SQLite (default), PostgreSQL, and MySQL support
- **Configurable Architecture**: Environment-based configuration
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Docker Support**: Containerized deployment with docker-compose
- **Database Monitoring**: Built-in database size checking and monitoring
- **Data Retention**: Configurable data retention policies

## Project Structure

```
├── config/              # Configuration management
├── db/                  # Database models and connection
├── models/              # Data models for market data
├── services/            # Core business logic
│   ├── websocket_client.py
│   ├── data_processor.py
│   └── db_size_checker.py
├── utils/               # Utility functions and helpers
├── tests/               # Test suite
├── main.py              # Application entry point
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-service deployment
└── pyproject.toml       # Project dependencies
```

## Installation

### Prerequisites

- Python 3.12 or higher
- UV package manager (recommended) or pip

### Using UV (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trad-save-history
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   uv run python main.py
   ```

### Using pip

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trad-save-history
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure and run**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   python main.py
   ```

## Configuration

The application is configured through environment variables. Copy `.env.example` to `.env` and modify the settings:

### Bybit API Configuration
- `BYBIT_API_KEY`: Your Bybit API key (optional for public streams)
- `BYBIT_API_SECRET`: Your Bybit API secret (optional for public streams)
- `USE_TESTNET`: Set to "True" to use Bybit's testnet environment

### WebSocket Configuration
- `WS_PRIVATE`: Set to "True" to use private WebSocket streams (requires API credentials)
- `SYMBOLS`: Comma-separated list of symbols (e.g., "BTCUSDT,ETHUSDT,LTCUSDT,SOLUSDT")
- `CHANNELS`: Comma-separated list of channels (e.g., "orderbook.50,trade,kline.1m")

### Database Configuration
- `DB_TYPE`: Database type (sqlite, postgresql, mysql)
- `DB_HOST`: Database host (for PostgreSQL/MySQL)
- `DB_PORT`: Database port (for PostgreSQL/MySQL)
- `DB_NAME`: Database name
- `DB_USER`: Database username (for PostgreSQL/MySQL)
- `DB_PASSWORD`: Database password (for PostgreSQL/MySQL)
- `DATABASE_URL`: Full SQLAlchemy database URL (overrides individual settings)

### Application Configuration
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `DATA_RETENTION_DAYS`: Number of days to retain data
- `TICKER_BATCH_SIZE`: Number of records to batch before saving
- `DB_SIZE_CHECK_INTERVAL`: Database size check interval in minutes

## Usage

### Local Development

Start the application:
```bash
python main.py
```

The application will:
1. Initialize the database and create tables
2. Connect to Bybit's WebSocket API
3. Subscribe to configured channels and symbols
4. Process and store incoming data
5. Run continuously until interrupted (Ctrl+C)

### Docker Deployment

1. **Build and run with docker-compose**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the application**
   ```bash
   docker-compose down
   ```

### Database Setup

The application automatically creates the necessary database tables on startup. Supported databases:

- **SQLite** (default): File-based database, no additional setup required
- **PostgreSQL**: Requires PostgreSQL server and credentials
- **MySQL**: Requires MySQL server and credentials

## Database Schema

The application stores three types of market data:

### Orderbooks
- Real-time orderbook snapshots
- Bid/ask price levels and quantities
- Timestamp and symbol information

### Trades
- Individual trade records
- Price, quantity, and side information
- Trade timestamps

### Klines
- Candlestick/OHLCV data
- Configurable timeframes (1m, 5m, 15m, etc.)
- Open, high, low, close prices and volume

## Development

### Running Tests

```bash
# Using UV
uv run pytest

# Using pip
pytest
```

### Code Quality

The project uses Ruff for code formatting and linting:

```bash
# Format code
uv run ruff format

# Check code quality
uv run ruff check
```

### Database Utilities

Check database connection and size:
```bash
python utils/check_db.py
```

## Monitoring

The application includes built-in monitoring features:

- **Database Size Monitoring**: Automatic database size checking
- **Logging**: Comprehensive logging with configurable levels
- **Error Recovery**: Automatic reconnection on WebSocket disconnection
- **Data Retention**: Configurable data cleanup policies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure code quality with Ruff
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the configuration examples in `.env.example`
- Review the test files for usage examples