import logging
import time

from sqlalchemy import insert

from db.database import SessionLocal
from models.market_data import TickerData

# from services.db_size_checker import DBSizeChecker

logger = logging.getLogger("bybit_collector.processor")


class DataProcessor:
    def __init__(self):
        # self.save_queue = asyncio.Queue()
        # self.db_size_checker = DBSizeChecker()
        # asyncio.create_task(self._save_worker())
        pass

    # async def add_to_save_queue(self, data_to_save):
    #     await self.save_queue.put(data_to_save)

    # async def _save_worker(self):
    #     """Worker that processes save operations."""
    #     while True:
    #         data_to_save = await self.save_queue.get()
    #         if data_to_save is None:  # Shutdown signal
    #             break
    #         try:
    #             await self.save_to_database(data_to_save)
    #         except Exception as e:
    #             logger.error(f"Error in save worker: {e}")
    #         finally:
    #             self.save_queue.task_done()

    # async def stop(self):
    #     # Signal save worker to stop
    #     await self.save_queue.put(None)
    #     await self.save_queue.join()

    def get_ticker_objects(self, data_to_save):
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
        return ticker_objects

    async def save_to_database(self, data_to_save):
        """Save ticker data to database synchronously."""
        start_time = time.time()
        try:
            # Get a database session from the generator
            async with SessionLocal() as session:
                async with session.begin():
                    ticker_objects = self.get_ticker_objects(data_to_save)
                    await session.execute(insert(TickerData), ticker_objects)

                # Check database size after saving
                # self.db_size_checker.check_db_size()

        except Exception as e:
            logger.error(f"Error getting database session: {e}")
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Database save execution time: {execution_time:.4f} seconds "
                        f"for {len(data_to_save)} records")
