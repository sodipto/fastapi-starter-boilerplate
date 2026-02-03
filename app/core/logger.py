"""
Production-ready logging configuration for FastAPI.

This module provides centralized logging configuration that:
- Supports log levels via LOG_LEVEL environment variable
- Integrates with Uvicorn logs
- Prevents duplicate log entries
- Works for both development and production modes

Usage:
    from app.core.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Application started")
    logger.error("An error occurred", exc_info=True)
"""

import logging
import sys
from typing import Optional


class FlushStreamHandler(logging.StreamHandler):
    """StreamHandler that flushes after every emit."""
    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the entire application.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = log_level.upper()
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        log_level = "INFO"
    
    numeric_level = getattr(logging, log_level)
    
    # Create handler with formatting
    handler = FlushStreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.handlers = [handler]
    
    # IMPORTANT: Re-enable the 'app' logger hierarchy (Alembic disables existing loggers)
    # This must re-enable all app.* loggers that were created before this function runs
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("app"):
            app_logger = logging.getLogger(name)
            app_logger.disabled = False
    
    # Quiet noisy third-party loggers
    for name in ["sqlalchemy.engine", "alembic", "httpcore", "httpx", "asyncio", "apscheduler"]:
        logging.getLogger(name).setLevel(logging.WARNING)
    
    # Configure uvicorn loggers to not duplicate
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvi_logger = logging.getLogger(name)
        uvi_logger.handlers = []
        uvi_logger.propagate = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: The name for the logger, typically __name__
        
    Returns:
        A configured Logger instance
    """
    return logging.getLogger(name)
