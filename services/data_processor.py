import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from db.database import get_db
from models.market_data import TickerData
from services.db_size_checker import DBSizeChecker

logger = logging.getLogger("bybit_collector.processor")


class DataProcessor:
    def __init__(self):
        self._save_thread = None
        self._save_queue = Queue()
        self._db_size_checker = DBSizeChecker()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._start_save_thread()
        logger.info("DataProcessor initialized with save thread and queue")

    def add_to_save_queue(self, data_to_save):
        """Add data to the save queue."""
        logger.info(f"Adding {len(data_to_save)} records to save queue")
        self._save_queue.put(data_to_save)
        logger.debug(f"Current queue size: {self._save_queue.qsize()}")

    def _start_save_thread(self):
        """Start the save thread."""
        logger.info("Starting save thread")
        self._save_thread = threading.Thread(target=self._save_worker, daemon=True)
        self._save_thread.start()
        logger.info("Save thread started successfully")

    def _save_worker(self):
        """Worker thread that processes save operations."""
        logger.info("Save worker thread started")
        while True:
            logger.debug("Waiting for data in save queue...")
            data_to_save = self._save_queue.get()
            if data_to_save is None:  # Shutdown signal
                logger.info("Received shutdown signal in save worker")
                break
            try:
                logger.info(f"Processing batch of {len(data_to_save)} records")
                self._save_to_database(data_to_save)
                logger.info(f"Successfully processed batch of {len(data_to_save)} records")
            except Exception as e:
                logger.error(f"Error in save thread: {e}", exc_info=True)
            finally:
                self._save_queue.task_done()
                logger.debug("Task marked as done in save queue")

    def stop(self):
        """Stop the data processor and cleanup resources."""
        logger.info("Stopping DataProcessor...")
        # Signal save thread to stop
        self._save_queue.put(None)
        if self._save_thread:
            logger.info("Waiting for save thread to finish...")
            self._save_thread.join()
            logger.info("Save thread stopped")
        self._executor.shutdown(wait=True)
        logger.info("DataProcessor stopped successfully")

    def _save_to_database(self, data_to_save):
        """Save ticker data to database synchronously."""
        start_time = time.time()
        logger.info(f"Starting database save operation for {len(data_to_save)} records")
        try:
            # Get a database session from the generator
            logger.debug("Getting database session")
            db = next(get_db())
            try:
                ticker_objects = []
                logger.debug("Creating ticker objects")
                for data in data_to_save:
                    ticker = TickerData(
                        timestamp=data['timestamp'],
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
                logger.debug(f"Created {len(ticker_objects)} ticker objects")

                logger.info("Performing bulk save operation")
                db.bulk_save_objects(ticker_objects)
                logger.debug("Committing transaction")
                db.commit()
                logger.info("Successfully committed transaction")

                # Check database size after saving
                logger.debug("Checking database size")
                self._db_size_checker.check_db_size()

            except Exception as e:
                logger.error(f"Error saving ticker data: {e}", exc_info=True)
                logger.info("Rolling back transaction")
                db.rollback()
                raise
            finally:
                logger.debug("Closing database session")
                db.close()

        except Exception as e:
            logger.error(f"Error getting database session: {e}", exc_info=True)
            raise
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Database save operation completed in {execution_time:.4f} seconds "
                        f"for {len(data_to_save)} records")
