from datetime import datetime
import logging
from typing import Callable, Any, Union
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import ThreadPoolExecutor

from app.services.interfaces.scheduler_service_interface import ISchedulerService


logger = logging.getLogger(__name__)


class SchedulerService(ISchedulerService):
    """
    Background task scheduler service using APScheduler.
    
    Supports both cron expressions and interval-based scheduling.
    Jobs can be registered before or after the scheduler is started.
    """

    def __init__(self):
        # Configure job stores
        jobstores = {
            'default': MemoryJobStore()
        }
        
        # Configure executors
        executors = {
            'default': AsyncIOExecutor(),
            'threadpool': ThreadPoolExecutor(max_workers=10)
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': True,  # Combine multiple pending executions of the same job
            'max_instances': 1,  # Only one instance of each job can run at a time
            'misfire_grace_time': 60  # Seconds after the designated runtime that the job is still allowed to run
        }
        
        self._scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        self._is_running = False

    def _parse_cron_expression(self, cron_expression: str) -> dict:
        """
        Parse a cron expression string into APScheduler CronTrigger parameters.
        
        Supports two formats:
        - 5-field format: "minute hour day month day_of_week"
        - 6-field format: "second minute hour day month day_of_week"
        
        Args:
            cron_expression: Cron expression string
            
        Returns:
            Dictionary with cron parameters for CronTrigger
        """
        parts = cron_expression.strip().split()
        
        if len(parts) == 5:
            # Standard 5-field cron: minute hour day month day_of_week
            return {
                'minute': parts[0],
                'hour': parts[1],
                'day': parts[2],
                'month': parts[3],
                'day_of_week': parts[4]
            }
        elif len(parts) == 6:
            # Extended 6-field cron: second minute hour day month day_of_week
            return {
                'second': parts[0],
                'minute': parts[1],
                'hour': parts[2],
                'day': parts[3],
                'month': parts[4],
                'day_of_week': parts[5]
            }
        else:
            raise ValueError(
                f"Invalid cron expression: '{cron_expression}'. "
                "Expected 5 or 6 space-separated fields."
            )

    def register_job(
        self,
        job_id: str,
        func: Callable[..., Any],
        cron_expression: str,
        *args,
        **kwargs
    ) -> None:
        """
        Register a job with a cron expression.
        
        Args:
            job_id: Unique identifier for the job
            func: The function to execute (can be sync or async)
            cron_expression: Cron expression string
                - 5-field format: "minute hour day month day_of_week"
                - 6-field format: "second minute hour day month day_of_week"
                
        Examples:
            - "0 0 * * *": Every day at midnight
            - "*/5 * * * *": Every 5 minutes
            - "0 9 * * 1-5": Every weekday at 9 AM
            - "0 0 1 * *": First day of every month at midnight
            - "30 0 8 * * 1-5": Every weekday at 8:00:30 AM (6-field format)
        """
        try:
            cron_params = self._parse_cron_expression(cron_expression)
            trigger = CronTrigger(**cron_params)
            
            self._scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=True
            )
            logger.info(f"Registered cron job '{job_id}' with expression '{cron_expression}'")
        except Exception as e:
            logger.error(f"Failed to register job '{job_id}': {e}")
            raise

    def schedule_once(
        self,
        job_id: str,
        func: Callable[..., Any],
        run_at: datetime,
        *args,
        **kwargs
    ) -> None:
        """
        Schedule a one-time job to run at a specific datetime.
        
        Args:
            job_id: Unique identifier for the job
            func: The function to execute (can be sync or async)
            run_at: The datetime when the job should run
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Examples:
            # Run 10 seconds from now
            scheduler.schedule_once(
                "send_email_123",
                send_email_func,
                datetime.now(timezone.utc) + timedelta(seconds=10),
                email="user@example.com"
            )
            
            # Run at a specific time
            scheduler.schedule_once(
                "report_job",
                generate_report,
                datetime(2026, 2, 1, 9, 0, 0, tzinfo=timezone.utc)
            )
        """
        try:
            trigger = DateTrigger(run_date=run_at)
            
            self._scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                args=args,
                kwargs=kwargs,
                replace_existing=True
            )
            logger.info(f"Scheduled one-time job '{job_id}' to run at {run_at.isoformat()}")
        except Exception as e:
            logger.error(f"Failed to schedule one-time job '{job_id}': {e}")
            raise

    def start(self) -> None:
        """Start the scheduler."""
        if not self._is_running:
            self._scheduler.start()
            self._is_running = True

    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        if self._is_running:
            self._scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("Scheduler shut down")

    def pause_job(self, job_id: str) -> None:
        """Pause a specific job."""
        try:
            self._scheduler.pause_job(job_id)
            logger.info(f"Paused job '{job_id}'")
        except Exception as e:
            logger.error(f"Failed to pause job '{job_id}': {e}")
            raise

    def resume_job(self, job_id: str) -> None:
        """Resume a paused job."""
        try:
            self._scheduler.resume_job(job_id)
            logger.info(f"Resumed job '{job_id}'")
        except Exception as e:
            logger.error(f"Failed to resume job '{job_id}': {e}")
            raise

    def remove_job(self, job_id: str) -> None:
        """Remove a job from the scheduler."""
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"Removed job '{job_id}'")
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {e}")
            raise

    def get_jobs(self) -> list:
        """Get all registered jobs."""
        return self._scheduler.get_jobs()

    @property
    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._is_running
