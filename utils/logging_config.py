import logging
import sys

from config.settings import LOG_LEVEL


def setup_logging():
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("bybit_collector.log")
        ]
    )
    
    # Create logger for the application
    logger = logging.getLogger("bybit_collector")
    logger.setLevel(log_level)
    
    return logger