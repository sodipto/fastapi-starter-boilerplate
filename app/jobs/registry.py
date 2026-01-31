"""
Job Registry

Central registry for all background jobs. Add new jobs to REGISTERED_JOBS list.

Cron Expression Format:
- 5-field: "minute hour day month day_of_week"
- 6-field: "second minute hour day month day_of_week"

Examples:
- "0 0 * * *": Every day at midnight
- "*/5 * * * *": Every 5 minutes
- "0 9 * * 1-5": Every weekday at 9 AM
- "0 0 1 * *": First day of every month at midnight
"""

from typing import Any, Callable, TypedDict

from app.jobs.health_check import health_check_job

class CronJobConfig(TypedDict):
    """Configuration for a cron-based job."""
    job_id: str
    func: Callable[..., Any]
    cron_expression: str
    enabled: bool


# ============================================================================
# REGISTERED JOBS
# Add your jobs here
# ============================================================================

REGISTERED_JOBS: list[CronJobConfig] = [
    {
        "job_id": "health_check",
        "func": health_check_job,
        "cron_expression": "*/1 * * * *",  # Every 1 minute
        "enabled": True,
    },
]


def register_all_jobs(scheduler_service) -> None:
    """
    Register all enabled jobs with the scheduler service.
    
    Args:
        scheduler_service: The SchedulerService instance
    """
    for job_config in REGISTERED_JOBS:
        if job_config["enabled"]:
            try:
                scheduler_service.register_job(
                    job_id=job_config["job_id"],
                    func=job_config["func"],
                    cron_expression=job_config["cron_expression"]
                )
                print(f"[Jobs] Registered job: {job_config['job_id']}")
            except Exception as e:
                print(f"[Jobs] Failed to register job {job_config['job_id']}: {e}")
