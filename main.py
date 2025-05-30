import signal
import sys
import time
from contextlib import contextmanager
from sqlalchemy.orm import Session

from db.database import engine, Base, SessionLocal
from utils.logging_config import setup_logging
from services.websocket_client import BybitWebSocketClient
from services.data_processor import DataProcessor

# Setup logging
logger = setup_logging()


def cleanup(ws_client):
    """Clean up resources before exiting."""
    logger.info("Shutting down...")
    if ws_client:
        ws_client.disconnect()
    logger.info("Application stopped")


# @contextmanager
# def get_db_session():
#     """Provide a transactional scope around a series of operations."""
#     session = SessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()


def main():
    """Main application entry point."""
    ws_client = None

    try:
        # Create database tables if they don't exist
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)

        # Create database session
        # with get_db_session() as db_session:
            # Initialize data processor
        data_processor = DataProcessor()

        # Define message handler
        def handle_ws_message(channel_type, message):
            data_processor.process_message(channel_type, message)

        # Initialize WebSocket client
        logger.info("Initializing WebSocket client...")
        ws_client = BybitWebSocketClient(handle_ws_message)

        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down...")
            cleanup(ws_client)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Connect to WebSocket
        logger.info("Connecting to Bybit WebSocket API...")
        ws_client.connect_public()

        # Keep the process running
        logger.info("Application started successfully. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except Exception as e:
        logger.exception(f"Application error: {e}")
    finally:
        cleanup(ws_client)


if __name__ == "__main__":
    main()
