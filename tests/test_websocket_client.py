import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest


@pytest.fixture()
def ws_client(monkeypatch):
    import types

    monkeypatch.setenv("TICKER_BATCH_SIZE", "2")

    pybit_stub = types.ModuleType("pybit")
    unified = types.ModuleType("unified_trading")
    unified.WebSocket = MagicMock()
    pybit_stub.unified_trading = unified
    sys.modules["pybit"] = pybit_stub
    sys.modules["pybit.unified_trading"] = unified

    processor_stub = types.ModuleType("services.data_processor")

    class FakeDataProcessor:
        def add_to_save_queue(self, data):
            pass

        def stop(self):
            pass

    processor_stub.DataProcessor = FakeDataProcessor
    sys.modules["services.data_processor"] = processor_stub

    import config.settings as settings
    import services.websocket_client as websocket_client

    importlib.reload(settings)
    importlib.reload(websocket_client)

    mock_processor = MagicMock()
    monkeypatch.setattr(websocket_client, "DataProcessor", lambda: mock_processor)

    client = websocket_client.BybitWebSocketClient()
    return client, mock_processor


def test_handle_ticker_batches_and_queues(ws_client):
    client, mock_processor = ws_client

    msg1 = {"data": {"symbol": "BTCUSDT", "lastPrice": "100"}}
    msg_same = {"data": {"symbol": "BTCUSDT", "lastPrice": "100"}}
    msg_change = {"data": {"symbol": "BTCUSDT", "lastPrice": "101"}}

    client.handle_ticker(msg1)
    assert len(client.ticker_data["BTCUSDT"]) == 1
    assert mock_processor.add_to_save_queue.call_count == 0

    client.handle_ticker(msg_same)
    assert len(client.ticker_data["BTCUSDT"]) == 1
    assert mock_processor.add_to_save_queue.call_count == 0

    client.handle_ticker(msg_change)
    assert client.ticker_data["BTCUSDT"] == []
    assert mock_processor.add_to_save_queue.call_count == 1

    queued = mock_processor.add_to_save_queue.call_args[0][0]
    assert len(queued) == 2
    assert [d["lastPrice"] for d in queued] == ["100", "101"]
    assert all(d["symbol"] == "BTCUSDT" for d in queued)
