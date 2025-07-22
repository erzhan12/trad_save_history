import importlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
pytest.importorskip("sqlalchemy")


@pytest.fixture()
def processor(tmp_path, monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    db_path = tmp_path / "test_db"
    monkeypatch.setenv("DB_TYPE", "sqlite")
    monkeypatch.setenv("DB_NAME", str(db_path))
    monkeypatch.setenv("ECHO_SQL", "False")

    import config.settings as settings
    import db.database as database
    import models.market_data as market_data
    import services.data_processor as data_processor
    import services.db_size_checker as db_size_checker

    importlib.reload(settings)
    importlib.reload(database)
    importlib.reload(market_data)
    importlib.reload(db_size_checker)
    importlib.reload(data_processor)

    database.Base.metadata.create_all(bind=database.engine)

    proc = data_processor.DataProcessor()
    yield proc
    proc.stop()
    database.Base.metadata.drop_all(bind=database.engine)



def make_sample_data():
    now = datetime.now(timezone.utc)
    return [
        {
            'timestamp': now,
            'symbol': 'BTCUSDT',
            'tickDirection': 'PlusTick',
            'price24hPcnt': 0.1,
            'lastPrice': 45000,
            'prevPrice24h': 44000,
            'highPrice24h': 46000,
            'lowPrice24h': 43000,
            'prevPrice1h': 44800,
            'markPrice': 45010,
            'indexPrice': 45005,
            'openInterest': 100.0,
            'openInterestValue': 1000.0,
            'turnover24h': 1000000.0,
            'volume24h': 2000.0,
            'nextFundingTime': 1700000000,
            'fundingRate': 0.0001,
            'bid1Price': 45000,
            'bid1Size': 1,
            'ask1Price': 45010,
            'ask1Size': 1,
        },
        {
            'timestamp': now,
            'symbol': 'ETHUSDT',
            'tickDirection': 'ZeroPlusTick',
            'price24hPcnt': 0.2,
            'lastPrice': 3000,
            'prevPrice24h': 2950,
            'highPrice24h': 3050,
            'lowPrice24h': 2900,
            'prevPrice1h': 2990,
            'markPrice': 3005,
            'indexPrice': 3002,
            'openInterest': 200.0,
            'openInterestValue': 6000.0,
            'turnover24h': 2000000.0,
            'volume24h': 4000.0,
            'nextFundingTime': 1700000000,
            'fundingRate': 0.0002,
            'bid1Price': 3000,
            'bid1Size': 2,
            'ask1Price': 3005,
            'ask1Size': 2,
        },
    ]



def test_add_to_save_queue_and_persistence(processor):
    from db.database import SessionLocal
    from models.market_data import TickerData

    sample_data = make_sample_data()
    processor.add_to_save_queue(sample_data)

    # Wait for the save worker to process the queue
    processor._save_queue.join()

    with SessionLocal() as session:
        records = session.query(TickerData).all()
        assert len(records) == len(sample_data)
        symbols = {r.symbol for r in records}
        assert {'BTCUSDT', 'ETHUSDT'} == symbols
