# Seq Logging Integration

This FastAPI boilerplate includes integrated Seq logging for centralized log management and analysis.

## What is Seq?

Seq is a centralized log management system that allows you to search, analyze, and monitor your application logs in real-time with a powerful query language and visualization tools.

## Setup

### 1. Install Seq Locally

If you don't have Seq installed, download it from: https://datalust.co/seq

Or run it using Docker:
```bash
docker run --name seq -d --restart unless-stopped -e ACCEPT_EULA=Y -p 5341:80 datalust/seq:latest
```

Access Seq UI at: http://localhost:5341

### 2. Enable Seq in Your Application

Update your `.env.development` file:

```env
# Seq logging settings
SEQ_ENABLED=True
SEQ_SERVER_URL=http://localhost:5341
SEQ_API_KEY=  # Optional: Add an API key if you've configured one in Seq
```

### 3. Install Dependencies

The seqlog package should already be installed. If not:
```bash
pip install seqlog
```

## Configuration

All Seq settings are in `app/core/config.py`:

- **SEQ_ENABLED**: Enable/disable Seq logging (default: False)
- **SEQ_SERVER_URL**: Seq server URL (default: http://localhost:5341)
- **SEQ_API_KEY**: Optional API key for authentication (default: empty)

## What Gets Logged to Seq

All application logs are automatically sent to Seq when enabled:

### 1. Custom Exceptions (401, 403, 404, 409, etc.)
```json
{
  "level": "Error",
  "message": "[LogID: xxx] UnauthorizedException - Status: 401 - Path: POST /api/v1/auth/login - Messages: {...}",
  "logId": "xxx",
  "statusCode": 401,
  "type": "UnauthorizedException",
  "path": "POST /api/v1/auth/login"
}
```

### 2. Unhandled Exceptions (500)
```json
{
  "level": "Error",
  "message": "[LogID: xxx] Unhandled exception - Path: GET /api/v1/users",
  "exception": "Full stack trace...",
  "logId": "xxx"
}
```

### 3. Application Events
- Application startup/shutdown
- Database migrations
- Background job execution
- Cache service operations
- Email sending events

## Using Seq

### View Logs in Seq UI

1. Open http://localhost:5341 in your browser
2. All logs will appear in real-time

### Search and Filter

Use Seq's powerful query language:

```sql
-- Find all errors
level == 'Error'

-- Find specific exception types
type == 'UnauthorizedException'

-- Find by log ID
logId == '9196f359-0ab3-4da1-be23-51045838a1ed'

-- Find by HTTP status code
statusCode >= 400

-- Find by path
path like '%/auth/%'

-- Combine filters
level == 'Error' and statusCode == 500
```

### Create Alerts

In Seq, you can create alerts for:
- All 500 errors
- Authentication failures
- Specific exception types
- Performance issues

## Adding Custom Properties to Logs

To add structured data to your logs:

```python
from app.core.logger import get_logger

logger = get_logger(__name__)

# Add extra context
logger.info(
    "User logged in",
    extra={
        "user_id": user.id,
        "email": user.email,
        "ip_address": request.client.host
    }
)
```

These properties will be searchable in Seq!

## Production Deployment

For production environments:

1. Deploy Seq on a dedicated server
2. Update `SEQ_SERVER_URL` in `.env.production`
3. Set `SEQ_API_KEY` for security
4. Configure retention policies in Seq
5. Set up alerts and dashboards

## Troubleshooting

### Logs not appearing in Seq?

1. Check if Seq is running: `docker ps` or visit http://localhost:5341
2. Verify `SEQ_ENABLED=True` in your .env file
3. Check application logs for Seq connection errors
4. Ensure seqlog package is installed: `pip list | grep seqlog`

### Performance Concerns?

Seq logging is configured with:
- Batch size: 10 logs
- Auto flush timeout: 2 seconds
- Async sending to avoid blocking your application

## Disable Seq Logging

Set in your `.env` file:
```env
SEQ_ENABLED=False
```

Logs will only go to console when disabled.
