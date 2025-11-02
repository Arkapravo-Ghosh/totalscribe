"""Logging configuration."""
import logging
from configs.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def setup_logger(name: str = __name__) -> logging.Logger:
    """Set up and return a logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger("soap_backend")
