"""
Background Jobs Package

This package contains all background job definitions and the job registry.
Jobs are automatically registered with the scheduler service on application startup.
"""

from app.jobs.registry import register_all_jobs, REGISTERED_JOBS, CronJobConfig

__all__ = ["register_all_jobs", "REGISTERED_JOBS", "CronJobConfig"]
