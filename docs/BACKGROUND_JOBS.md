# Background Jobs

Schedule and run background tasks using APScheduler.

## Table of Contents

- [Configuration](#configuration)
- [Creating Jobs](#creating-jobs)
- [Cron Expressions](#cron-expressions)
- [Scheduler API](#scheduler-api)

---

## Configuration

Enable the scheduler in your `.env` file:

```env
BACKGROUND_JOBS_ENABLED=True
```

Jobs are registered in `app/jobs/registry.py` and start automatically when the application boots.

---

## Creating Jobs

### Step 1: Create the Job Function

Create a new file in `app/jobs/`:

```python
# app/jobs/cleanup.py
from datetime import datetime, timezone

async def cleanup_expired_tokens() -> None:
    """Remove expired tokens from the database."""
    print(f"Cleanup running at {datetime.now(timezone.utc).isoformat()}")
    # Your cleanup logic here
```

### Step 2: Register the Job

Add your job to `REGISTERED_JOBS` in `app/jobs/registry.py`:

```python
from app.jobs.cleanup import cleanup_expired_tokens

REGISTERED_JOBS: list[CronJobConfig] = [
    {
        "job_id": "cleanup_expired_tokens",
        "func": cleanup_expired_tokens,
        "cron_expression": "0 0 * * *",  # Daily at midnight
        "enabled": True,
    },
]
```

### Disabling a Job

Set `enabled: False` to disable without removing:

```python
{
    "job_id": "my_job",
    "func": my_job_func,
    "cron_expression": "0 0 * * *",
    "enabled": False,
}
```

---

## Cron Expressions

### 5-Field Format

```
┌─────────── minute (0-59)
│ ┌───────── hour (0-23)
│ │ ┌─────── day of month (1-31)
│ │ │ ┌───── month (1-12)
│ │ │ │ ┌─── day of week (0-6, Sun=0)
* * * * *
```

### Common Patterns

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Daily at midnight |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 0 1 * *` | First of month |

---

## Scheduler API

### Using SchedulerService

```python
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
from app.services.scheduler_service import SchedulerService

@inject
async def manage_jobs(
    scheduler: SchedulerService = Provide[Container.scheduler_service]
):
    # Register dynamically
    scheduler.register_job(
        job_id="dynamic_job",
        func=my_function,
        cron_expression="0 */6 * * *"
    )
    
    # Get all jobs
    jobs = scheduler.get_jobs()
    
    # Pause/resume
    scheduler.pause_job("my_job_id")
    scheduler.resume_job("my_job_id")
    
    # Remove
    scheduler.remove_job("my_job_id")
```

### Available Methods

| Method | Description |
|--------|-------------|
| `register_job(job_id, func, cron_expression)` | Register a cron job |
| `start()` | Start the scheduler |
| `shutdown()` | Shutdown gracefully |
| `pause_job(job_id)` | Pause a job |
| `resume_job(job_id)` | Resume a paused job |
| `remove_job(job_id)` | Remove a job |
| `get_jobs()` | List all jobs |
| `is_running` | Check if scheduler is running |

---

## Best Practices

1. **Keep jobs lightweight** — offload heavy work to task queues
2. **Handle exceptions** — wrap logic in try-except
3. **Use unique job IDs** — must be unique across the app
4. **Log execution** — track when jobs run
5. **One job per file** — improves organization and testing
