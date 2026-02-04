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
try:
    import seqlog
    SEQ_AVAILABLE = True
except ImportError:
    SEQ_AVAILABLE = False


class FlushStreamHandler(logging.StreamHandler):
    """StreamHandler that flushes after every emit."""
    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logging(log_level: str = "INFO", seq_server_url: str = None, seq_api_key: str = None) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        seq_server_url: Seq server URL (e.g., http://localhost:5341)
        seq_api_key: Optional Seq API key for authentication
    """
    log_level = log_level.upper()
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        log_level = "INFO"
    
    numeric_level = getattr(logging, log_level)
    
    # Configure root logger
    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.handlers = []  # Clear existing handlers
    
    # Create console handler with formatting
    console_handler = FlushStreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)
    
    # Configure Seq logging if enabled (add Seq handler alongside console)
    if seq_server_url and SEQ_AVAILABLE:
        try:
            # Get Seq handler
            seq_handler = seqlog.SeqLogHandler(
                server_url=seq_server_url,
                api_key=seq_api_key if seq_api_key else None,
                batch_size=10,
                auto_flush_timeout=2
            )
            seq_handler.setLevel(numeric_level)
            root.addHandler(seq_handler)
            root.info(f"Seq logging enabled: {seq_server_url}")
        except Exception as e:
            root.warning(f"Failed to configure Seq logging: {e}")
    elif seq_server_url and not SEQ_AVAILABLE:
        root.warning("Seq logging requested but seqlog package not installed. Install with: pip install seqlog")
    
    # IMPORTANT: Re-enable the 'app' logger hierarchy (Alembic disables existing loggers)
    # This must re-enable all app.* loggers that were created before this function runs
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("app"):
            app_logger = logging.getLogger(name)
            app_logger.disabled = False
    
    # Quiet noisy third-party loggers
    for name in ["sqlalchemy.engine", "alembic", "httpcore", "httpx", "asyncio", "apscheduler"]:
        logging.getLogger(name).setLevel(logging.WARNING)
    
    # Configure uvicorn loggers
    # Suppress uvicorn.access (HTTP request logs) to reduce noise in Seq
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Configure uvicorn error loggers to not duplicate
    for name in ["uvicorn", "uvicorn.error"]:
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
