"""
Health Check Job

Periodic health check to verify the scheduler is running properly.
"""


from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def health_check_job() -> None:
    """
    Health check that runs periodically.
    Logs the current timestamp to verify the scheduler is working.
    """
    logger.info(f"Scheduler heartbeat at {datetime.now(timezone.utc).isoformat()}")
