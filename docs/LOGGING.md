# Logging & Seq Integration

Structured logging with optional Seq server integration.

## Table of Contents

- [Configuration](#configuration)
- [Using Loggers](#using-loggers)
- [Seq Setup](#seq-setup)
- [Structured Properties](#structured-properties)
- [Troubleshooting](#troubleshooting)

---

## Configuration

```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
SEQ_ENABLED=False           # Enable Seq integration
SEQ_SERVER_URL=http://localhost:5341
SEQ_API_KEY=                # Optional, if Seq requires auth
```

---

## Using Loggers

### Get a Logger

```python
from app.core.logger import get_logger

logger = get_logger(__name__)

logger.info("User logged in", extra={"user_id": "123"})
logger.warning("Rate limit approaching", extra={"requests": 95})
logger.error("Payment failed", extra={"order_id": "456", "amount": 99.99})
```

### In Services

```python
class UserService:
    def __init__(self):
        self._logger = get_logger(__name__)
    
    async def create_user(self, data):
        self._logger.info("Creating user", extra={"email": data.email})
        # ...
```

---

## Seq Setup

### Run Seq with Docker

```bash
docker run -d \
  --name seq \
  --restart unless-stopped \
  -e ACCEPT_EULA=Y \
  -p 5341:80 \
  datalust/seq:latest
```

### Configure

```env
SEQ_ENABLED=True
SEQ_SERVER_URL=http://localhost:5341
```

### Access UI

Open http://localhost:5341 to view logs.

---

## Structured Properties

The middleware automatically logs structured fields:

| Property | Description |
|----------|-------------|
| `UserId` | Current user ID |
| `LogId` | Unique log correlation ID |
| `StatusCode` | HTTP status code |
| `Path` | Request path |
| `HttpMethod` | GET, POST, etc. |
| `ErrorInfo` | Exception details |
| `Type` | Exception type name |

### Seq Queries

```
StatusCode == 500
Type == "UnauthorizedException"
Path == "/api/v1/users"
UserId == "abc-123"
```

---

## Troubleshooting

### Logs Not Appearing in Seq

1. Verify `SEQ_ENABLED=True`
2. Check Seq is running: `curl http://localhost:5341/api`
3. Verify `seqlog` is installed: `pip show seqlog`

### Missing Structured Properties

Ensure `support_extra_properties=True` in `log_to_seq` call (already set in `logger.py`).

### Adjust Log Level

For more verbose output during debugging:

```env
LOG_LEVEL=DEBUG
```

---

## Log Levels

| Level | Use Case |
|-------|----------|
| `DEBUG` | Detailed diagnostic info |
| `INFO` | General operational events |
| `WARNING` | Unexpected but handled situations |
| `ERROR` | Errors requiring attention |
| `CRITICAL` | System-level failures |
