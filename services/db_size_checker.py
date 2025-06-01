import logging
import time

from sqlalchemy import text

from config.settings import DATABASE_URL, DB_SIZE_CHECK_INTERVAL
from db.database import engine

logger = logging.getLogger("bybit_collector.db_size_checker")


class DBSizeChecker:
    """Monitors and reports database size growth over time."""
    
    def __init__(self) -> None:
        """Initialize the database size checker."""
        self.last_db_size_check: float = time.time()
        self.initial_time: float = time.time()
        self.db_size_check_interval: int = DB_SIZE_CHECK_INTERVAL
        self.initial_db_size: float = self._get_db_size() / (1024 * 1024)  # Store initial size 
        logger.info(f"Initial database size: {self.initial_db_size:.2f} MB")

    def _get_sqlite_size(self) -> float:
        """Get the size of SQLite database in bytes."""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT page_count * page_size as size 
                FROM pragma_page_count(), pragma_page_size()
            """))
            return float(result.scalar())

    def _get_postgresql_size(self) -> float:
        """Get the size of PostgreSQL database in bytes."""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT pg_database_size(current_database())"))
            return float(result.scalar())

    def _get_db_size(self) -> float:
        """Get the size of the database in bytes."""
        try:
            if DATABASE_URL.startswith('sqlite'):
                return self._get_sqlite_size()
            elif DATABASE_URL.startswith('postgresql'):
                return self._get_postgresql_size()
            else:
                logger.warning("Database size check not implemented for this database type")
                return 0.0
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0.0

    def check_db_size(self) -> None:
        """Check and log database size if enough time has passed."""
        current_time = time.time()
        if current_time - self.last_db_size_check >= self.db_size_check_interval:
            current_size = self._get_db_size() / (1024 * 1024) 
            size_growth = current_size - self.initial_db_size
            elapsed_hours = (current_time - self.initial_time) / 3600
            logger.info(
                f"Database size: {current_size:.2f}  MB | "
                f"Growth since start: {size_growth:.2f} MB | "
                f"Elapsed time: {elapsed_hours:.2f} hours | "
                f"Growth rate: {size_growth / elapsed_hours:.2f} MB/hour"
            )
            self.last_db_size_check = current_time

    def stop(self) -> None:
        """Stop the database size checker."""
        logger.info("Database size checker stopped")