import os
import sys
from pathlib import Path

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Set up test environment variables before importing any modules
os.environ["DB_TYPE"] = "sqlite"
os.environ["DB_NAME"] = "test_bybit_data"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["USE_TESTNET"] = "True"
os.environ["WS_PRIVATE"] = "False"
os.environ["SYMBOLS"] = "BTCUSDT"
os.environ["CHANNELS"] = "trade"
os.environ["DATA_RETENTION_DAYS"] = "1"
os.environ["TICKER_BATCH_SIZE"] = "10"
os.environ["DB_SIZE_CHECK_INTERVAL"] = "1"

# Import modules after setting environment variables
from db.database import Base, engine


@pytest.fixture(scope="session")
def test_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up test database
    if os.path.exists("test_bybit_data.db"):
        os.remove("test_bybit_data.db")


@pytest.fixture(autouse=True)
def setup_test_env(test_database):
    """Set up test environment for each test."""
    yield 