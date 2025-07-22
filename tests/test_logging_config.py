import importlib
import logging
import sys
import types
from pathlib import Path


def test_setup_logging_adds_handlers(monkeypatch):
    # Ensure project root is on sys.path for module imports
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))

    # Provide a stub for python-dotenv so config.settings can be imported
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda: None)

    import utils.logging_config as logging_config
    importlib.reload(logging_config)

    # Remove existing handlers so basicConfig attaches ours
    root_logger = logging.getLogger()
    old_handlers = root_logger.handlers[:]
    root_logger.handlers.clear()

    monkeypatch.setattr(logging_config, "LOG_LEVEL", "DEBUG")

    logger = logging_config.setup_logging()

    try:
        assert logger.level == logging.DEBUG
        handler_types = {type(h) for h in root_logger.handlers}
        assert logging.FileHandler in handler_types
        assert logging.StreamHandler in handler_types
    finally:
        root_logger.handlers[:] = old_handlers
