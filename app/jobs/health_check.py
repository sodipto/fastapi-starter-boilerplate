"""
Health Check Job

Periodic health check to verify the scheduler is running properly.
"""

from datetime import datetime, timezone


async def health_check_job() -> None:
    """
    Health check that runs periodically.
    Logs the current timestamp to verify the scheduler is working.
    """
    print(f"[HealthCheck] Scheduler heartbeat at {datetime.now(timezone.utc).isoformat()}")
