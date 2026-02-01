# Background Task Scheduler

This document describes how to use the background task scheduler service in the FastAPI boilerplate.

## Overview

The scheduler service uses [APScheduler](https://apscheduler.readthedocs.io/) to run background tasks on a schedule. It supports:

- **Cron-based scheduling**: Run jobs at specific times using cron expressions
- **Async support**: Both synchronous and asynchronous job functions

## Configuration

The scheduler can be enabled/disabled via the `BACKGROUND_JOBS_ENABLED` setting in your `.env` file:

```env
BACKGROUND_JOBS_ENABLED=True
```

## Folder Structure

```
app/jobs/
├── __init__.py          # Package exports
├── registry.py          # Job registry and registration logic
├── health_check.py      # Health check job
└── cleanup.py           # Cleanup job
```

## Quick Start

The scheduler automatically starts when the application boots up (if `BACKGROUND_JOBS_ENABLED=True`). Jobs defined in `app/jobs/registry.py` are registered and executed according to their schedules.

## Adding New Jobs

### Step 1: Create Your Job File

Create a new file in `app/jobs/` folder (e.g., `app/jobs/my_job.py`):

```python
from datetime import datetime, timezone


async def my_custom_job() -> None:
    """Description of what your job does."""
    print(f"My custom job is running at {datetime.now(timezone.utc).isoformat()}")
    # Your job logic here
```

### Step 2: Register the Job

Import and add your job to the `REGISTERED_JOBS` list in `app/jobs/registry.py`:

```python
from app.jobs.my_job import my_custom_job

REGISTERED_JOBS: list[CronJobConfig] = [
    # ... existing jobs ...
    {
        "job_id": "my_custom_job",
        "func": my_custom_job,
        "cron_expression": "0 */2 * * *",  # Every 2 hours
        "enabled": True,
    },
]
```

## Cron Expression Format

The scheduler supports two cron formats:

### 5-Field Format (Standard)
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * *
```

### 6-Field Format (Extended)
```
┌───────────── second (0 - 59)
│ ┌───────────── minute (0 - 59)
│ │ ┌───────────── hour (0 - 23)
│ │ │ ┌───────────── day of month (1 - 31)
│ │ │ │ ┌───────────── month (1 - 12)
│ │ │ │ │ ┌───────────── day of week (0 - 6)
│ │ │ │ │ │
* * * * * *
```

### Common Examples

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Every day at midnight |
| `0 9 * * 1-5` | Every weekday at 9 AM |
| `0 0 1 * *` | First day of every month |
| `0 0 * * 0` | Every Sunday at midnight |
| `30 0 8 * * *` | Every day at 8:00:30 (6-field) |

## Using the Scheduler Service Programmatically

You can also use the scheduler service directly in your code:

```python
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
from app.services.scheduler_service import SchedulerService

@inject
async def some_endpoint(
    scheduler: SchedulerService = Provide[Container.scheduler_service]
):
    # Register a new job dynamically
    scheduler.register_job(
        job_id="dynamic_job",
        func=my_function,
        cron_expression="0 */6 * * *"
    )
    
    # Get all jobs
    jobs = scheduler.get_jobs()
    
    # Pause a job
    scheduler.pause_job("my_job_id")
    
    # Resume a job
    scheduler.resume_job("my_job_id")
    
    # Remove a job
    scheduler.remove_job("my_job_id")
```

## API Reference

### SchedulerService Methods

| Method | Description |
|--------|-------------|
| `register_job(job_id, func, cron_expression, *args, **kwargs)` | Register a cron-based job |
| `start()` | Start the scheduler |
| `shutdown()` | Shutdown the scheduler gracefully |
| `pause_job(job_id)` | Pause a specific job |
| `resume_job(job_id)` | Resume a paused job |
| `remove_job(job_id)` | Remove a job |
| `get_jobs()` | Get all registered jobs |
| `is_running` | Property to check if scheduler is running |

## Scheduler Configuration

The scheduler is configured with sensible defaults in `app/services/scheduler_service.py`:

- **Timezone**: UTC
- **Coalesce**: True (combines multiple pending executions)
- **Max Instances**: 1 (only one instance of each job runs at a time)
- **Misfire Grace Time**: 60 seconds
- **Thread Pool Workers**: 10 (for synchronous jobs)

## Best Practices

1. **Keep jobs lightweight**: Long-running tasks should be offloaded to a task queue (like Celery)
2. **Handle exceptions**: Always wrap your job logic in try-except blocks
3. **Use unique job IDs**: Job IDs must be unique across the application
4. **Log your jobs**: Use print or logging to track job execution
5. **Test jobs independently**: Jobs should be testable without the scheduler
6. **Use timezone-aware datetimes**: Use `datetime.now(timezone.utc)` instead of deprecated `datetime.utcnow()`
7. **One job per file**: Keep each job in its own file for better organization

## Disabling Jobs

To disable a job without removing it, set `enabled: False` in the job configuration:

```python
{
    "job_id": "my_job",
    "func": my_job_func,
    "cron_expression": "0 0 * * *",
    "enabled": False,  # This job won't run
}
```

## Disabling the Scheduler

To disable all background jobs, set in your `.env` file:

```env
BACKGROUND_JOBS_ENABLED=False
```
