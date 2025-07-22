import importlib
import sys
from pathlib import Path
import types

import pytest

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def reload_modules(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    # stub mysql connector so utils.db_connect can be imported without the
    # real dependency installed
    if 'mysql' not in sys.modules:
        mysql_mod = types.ModuleType('mysql')
        connector_mod = types.ModuleType('mysql.connector')
        connector_mod.connect = lambda *a, **k: None
        mysql_mod.connector = connector_mod
        sys.modules['mysql'] = mysql_mod
        sys.modules['mysql.connector'] = connector_mod

    if 'psycopg2' not in sys.modules:
        psycopg2_mod = types.ModuleType('psycopg2')
        psycopg2_mod.connect = lambda *a, **k: None
        sys.modules['psycopg2'] = psycopg2_mod

    import config.settings as settings
    import utils.db_connect as db_connect
    importlib.reload(settings)
    importlib.reload(db_connect)
    return db_connect


class DummyCursor:
    def __init__(self, size):
        self.size = size
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return (self.size,)

    def close(self):
        pass


class DummyConn:
    def __init__(self, size):
        self.cursor_obj = DummyCursor(size)

    def cursor(self):
        return self.cursor_obj

    def close(self):
        pass


def test_get_db_connection_sqlite(monkeypatch):
    db_connect = reload_modules(
        monkeypatch,
        DB_TYPE="sqlite",
        DB_NAME="test_db",
        DB_HOST="",
        DB_PORT="",
        DB_USER="",
        DB_PASSWORD="",
    )
    mock_obj = object()
    monkeypatch.setattr(db_connect.sqlite3, "connect", lambda path: mock_obj)
    assert db_connect.get_db_connection() is mock_obj


def test_get_db_connection_postgresql(monkeypatch):
    db_connect = reload_modules(
        monkeypatch,
        DB_TYPE="postgresql",
        DB_NAME="db",
        DB_HOST="host",
        DB_PORT="5432",
        DB_USER="user",
        DB_PASSWORD="pass",
    )
    mock_obj = object()

    def fake_connect(**kwargs):
        assert kwargs["host"] == "host"
        assert kwargs["port"] == "5432"
        assert kwargs["database"] == "db"
        assert kwargs["user"] == "user"
        assert kwargs["password"] == "pass"
        return mock_obj

    monkeypatch.setattr(db_connect.psycopg2, "connect", fake_connect)
    assert db_connect.get_db_connection() is mock_obj


def test_get_db_connection_mysql(monkeypatch):
    db_connect = reload_modules(
        monkeypatch,
        DB_TYPE="mysql",
        DB_NAME="db",
        DB_HOST="host",
        DB_PORT="3306",
        DB_USER="user",
        DB_PASSWORD="pass",
    )
    mock_obj = object()

    def fake_connect(**kwargs):
        assert kwargs["host"] == "host"
        assert kwargs["port"] == "3306"
        assert kwargs["database"] == "db"
        assert kwargs["user"] == "user"
        assert kwargs["password"] == "pass"
        return mock_obj

    monkeypatch.setattr(db_connect.mysql.connector, "connect", fake_connect)
    assert db_connect.get_db_connection() is mock_obj


def test_get_db_connection_invalid(monkeypatch):
    db_connect = reload_modules(monkeypatch, DB_TYPE="sqlite")
    db_connect.DB_TYPE = "oracle"
    with pytest.raises(ValueError):
        db_connect.get_db_connection()


def test_get_db_size_sqlite(monkeypatch):
    db_connect = reload_modules(monkeypatch, DB_TYPE="sqlite", DB_NAME="file")
    dummy = DummyConn(100)
    monkeypatch.setattr(db_connect.sqlite3, "connect", lambda path: dummy)
    assert db_connect.get_db_size() == 100
    assert dummy.cursor_obj.executed


def test_get_db_size_postgresql(monkeypatch):
    db_connect = reload_modules(monkeypatch, DB_TYPE="postgresql", DB_NAME="db")
    dummy = DummyConn(200)
    monkeypatch.setattr(db_connect.psycopg2, "connect", lambda **kw: dummy)
    assert db_connect.get_db_size() == 200
    assert dummy.cursor_obj.executed == [
        ("SELECT pg_database_size(current_database())", None)
    ]


def test_get_db_size_mysql(monkeypatch):
    db_connect = reload_modules(
        monkeypatch,
        DB_TYPE="mysql",
        DB_NAME="db",
    )
    dummy = DummyConn(300)
    monkeypatch.setattr(db_connect.mysql.connector, "connect", lambda **kw: dummy)
    assert db_connect.get_db_size() == 300
    executed_query, params = dummy.cursor_obj.executed[0]
    assert "information_schema.tables" in executed_query
    assert params == ("db",)


def test_get_db_size_invalid(monkeypatch):
    db_connect = reload_modules(monkeypatch, DB_TYPE="sqlite")
    db_connect.DB_TYPE = "oracle"
    with pytest.raises(ValueError):
        db_connect.get_db_size()
