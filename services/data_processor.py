import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from db.database import get_db

# from typing import Dict, Any
# from sqlalchemy.orm import Session
from models.market_data import TickerData
from services.db_size_checker import DBSizeChecker

logger = logging.getLogger("bybit_collector.processor")


class DataProcessor:
    def __init__(self):
        self.save_thread = None
        self.save_queue = Queue()
        self.db_size_checker = DBSizeChecker()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._start_save_thread()

    def _start_save_thread(self):
        """Start the save thread."""
        self.save_thread = threading.Thread(target=self._save_worker, daemon=True)
        self.save_thread.start()

    def _save_worker(self):
        """Worker thread that processes save operations."""
        while True:
            data_to_save = self.save_queue.get()
            if data_to_save is None:  # Shutdown signal
                break
            try:
                self._save_to_database(data_to_save)
            except Exception as e:
                logger.error(f"Error in save thread: {e}")
            finally:
                self.save_queue.task_done()

    def stop(self):
        # Signal save thread to stop
        self.save_queue.put(None)
        if self.save_thread:
            self.save_thread.join()
        self.executor.shutdown(wait=True)

    def _save_to_database(self, data_to_save):
        """Save ticker data to database synchronously."""
        start_time = time.time()
        try:
            # Get a database session from the generator
            db = next(get_db())
            try:
                ticker_objects = []
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

                db.bulk_save_objects(ticker_objects)
                db.commit()

                # Check database size after saving
                self.db_size_checker.check_db_size()

            except Exception as e:
                logger.error(f"Error saving ticker data: {e}")
                db.rollback()
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error getting database session: {e}")
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Database save execution time: {execution_time:.4f} seconds "
                        f"for {len(data_to_save)} records")
