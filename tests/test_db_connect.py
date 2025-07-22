import importlib
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def stub_db_libraries(monkeypatch):
    stub_mysql = types.ModuleType("mysql")
    stub_connector = types.ModuleType("mysql.connector")
    stub_mysql.connector = stub_connector
    monkeypatch.setitem(sys.modules, "mysql", stub_mysql)
    monkeypatch.setitem(sys.modules, "mysql.connector", stub_connector)
    monkeypatch.setitem(sys.modules, "psycopg2", types.ModuleType("psycopg2"))


@pytest.fixture()
def reload_db_connect():
    def _reload():
        import config.settings as settings
        import utils.db_connect as db_connect

        importlib.reload(settings)
        importlib.reload(db_connect)
        return db_connect

    return _reload


@pytest.fixture()
def set_env(monkeypatch):
    def _apply(db_type):
        monkeypatch.setenv("DB_TYPE", db_type)
        monkeypatch.setenv("DB_HOST", "host")
        monkeypatch.setenv("DB_PORT", "123")
        monkeypatch.setenv("DB_NAME", "name")
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "pass")

    return _apply


@pytest.mark.parametrize(
    "db_type, attr_path",
    [
        ("sqlite", "sqlite3.connect"),
        ("postgresql", "psycopg2.connect"),
        ("mysql", "mysql.connector.connect"),
    ],
)
def test_get_db_connection_returns_mock(monkeypatch, set_env, reload_db_connect, db_type, attr_path):
    set_env(db_type)
    db_connect = reload_db_connect()

    dummy = object()
    module_name, func_name = attr_path.split(".", 1)
    module = getattr(db_connect, module_name)
    for part in func_name.split(".")[:-1]:
        module = getattr(module, part)
    monkeypatch.setattr(module, func_name.split(".")[-1], lambda *a, **k: dummy, raising=False)

    conn = db_connect.get_db_connection()
    assert conn is dummy


def test_get_db_connection_invalid(monkeypatch, set_env, reload_db_connect):
    set_env("sqlite")
    db_connect = reload_db_connect()
    monkeypatch.setattr(db_connect, "DB_TYPE", "oracle")

    with pytest.raises(ValueError):
        db_connect.get_db_connection()


@pytest.mark.parametrize(
    "db_type, expected_sub",
    [
        ("sqlite", "page_count"),
        ("postgresql", "pg_database_size"),
        ("mysql", "information_schema.tables"),
    ],
)
def test_get_db_size(monkeypatch, set_env, reload_db_connect, db_type, expected_sub):
    set_env(db_type)
    db_connect = reload_db_connect()

    dummy_conn = MagicMock()
    dummy_cursor = MagicMock()
    dummy_conn.cursor.return_value = dummy_cursor
    dummy_cursor.fetchone.return_value = (99,)

    monkeypatch.setattr(db_connect, "get_db_connection", lambda: dummy_conn)

    size = db_connect.get_db_size()

    assert size == 99
    args, _ = dummy_cursor.execute.call_args
    assert expected_sub in args[0]
