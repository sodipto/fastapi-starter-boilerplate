from abc import ABC, abstractmethod
from typing import Callable, Any


class ISchedulerService(ABC):
    """Interface for the background task scheduler service."""

    @abstractmethod
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
            func: The function to execute
            cron_expression: Cron expression string (e.g., "0 0 * * *" for daily at midnight)
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        pass

    @abstractmethod
    def register_interval_job(
        self,
        job_id: str,
        func: Callable[..., Any],
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        *args,
        **kwargs
    ) -> None:
        """
        Register a job with an interval.
        
        Args:
            job_id: Unique identifier for the job
            func: The function to execute
            seconds: Interval in seconds
            minutes: Interval in minutes
            hours: Interval in hours
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """Start the scheduler."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        pass

    @abstractmethod
    def pause_job(self, job_id: str) -> None:
        """Pause a specific job."""
        pass

    @abstractmethod
    def resume_job(self, job_id: str) -> None:
        """Resume a paused job."""
        pass

    @abstractmethod
    def remove_job(self, job_id: str) -> None:
        """Remove a job from the scheduler."""
        pass

    @abstractmethod
    def get_jobs(self) -> list:
        """Get all registered jobs."""
        pass
