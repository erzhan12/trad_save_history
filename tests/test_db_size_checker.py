import sys
from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import db_size_checker


class DummyResult:
    def __init__(self, value):
        self._value = value

    def scalar(self):
        return self._value


class DummyConnection:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def execute(self, *args, **kwargs):
        return DummyResult(self.value)


@pytest.mark.parametrize(
    "db_url,expected",
    [
        ("sqlite:///x.db", 123),
        ("postgresql://localhost/db", 456),
    ],
)
def test_get_db_size_selects_helper(monkeypatch, db_url, expected):
    monkeypatch.setattr(db_size_checker, "DATABASE_URL", db_url)

    def fake_sqlite(self):
        return expected

    def fake_postgres(self):
        return expected

    monkeypatch.setattr(db_size_checker.DBSizeChecker, "_get_sqlite_size", fake_sqlite)
    monkeypatch.setattr(db_size_checker.DBSizeChecker, "_get_postgresql_size", fake_postgres)

    checker = db_size_checker.DBSizeChecker()
    result = checker._get_db_size()
    assert result == pytest.approx(expected)


def test_sqlite_size(monkeypatch):
    dummy_conn = DummyConnection(111)
    monkeypatch.setattr(db_size_checker.engine, "connect", lambda: dummy_conn)

    checker = db_size_checker.DBSizeChecker()
    assert checker._get_sqlite_size() == pytest.approx(111)


def test_postgresql_size(monkeypatch):
    dummy_conn = DummyConnection(222)
    monkeypatch.setattr(db_size_checker.engine, "connect", lambda: dummy_conn)

    checker = db_size_checker.DBSizeChecker()
    assert checker._get_postgresql_size() == pytest.approx(222)


def test_check_db_size_logging(monkeypatch):
    monkeypatch.setattr(db_size_checker, "DB_SIZE_CHECK_INTERVAL", 1)

    times = iter([0, 0, 0.5, 1.5, 2.5])
    monkeypatch.setattr(db_size_checker.time, "time", lambda: next(times))

    get_calls = []

    def fake_get(self):
        get_calls.append(True)
        return 1024

    monkeypatch.setattr(db_size_checker.DBSizeChecker, "_get_db_size", fake_get)

    logs = []
    monkeypatch.setattr(db_size_checker.logger, "info", lambda msg: logs.append(msg))

    checker = db_size_checker.DBSizeChecker()
    get_calls.clear()
    logs.clear()

    checker.check_db_size()  # interval not exceeded
    assert not get_calls
    assert not logs

    checker.check_db_size()  # interval exceeded
    assert get_calls
    assert logs
