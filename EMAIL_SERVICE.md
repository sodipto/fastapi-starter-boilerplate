# Email Service Documentation

## Overview

This FastAPI email sending service provides a robust, production-ready solution for sending emails with support for HTML content, attachments, CC/BCC recipients, and comprehensive logging.

## Features

- ✅ Async email sending using `aiosmtplib`
- ✅ Email validation before sending
- ✅ HTML email body support
- ✅ File attachments from disk
- ✅ TO, CC, and BCC recipients
- ✅ TLS/SSL configuration
- ✅ Comprehensive error handling
- ✅ Database logging of all email attempts
- ✅ Dependency injection using `dependency-injector`
- ✅ Clean, testable architecture with interfaces

## Architecture

### Components

1. **EmailService** (`app/services/email_service.py`)
   - Main service implementing email sending logic
   - Validates email addresses
   - Handles attachments
   - Logs all attempts to database

2. **EmailLogger Model** (`app/models/email_logger.py`)
   - SQLAlchemy ORM model for email logs
   - Stores: from, subject, body, recipients, status, errors

3. **Email Settings** (`app/core/config.py`)
   - Pydantic BaseSettings configuration
   - Environment-based configuration

4. **Email Repository** (`app/repositories/email_log_repository.py`)
   - Data access layer for email logs

## Configuration

Add the following environment variables to your `.env.{ENV}` file:

```env
# Email Configuration
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM_EMAIL=noreply@yourapp.com
MAIL_FROM_NAME=Your App Name
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

### Email Provider Examples

#### Gmail
```env
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
# Note: Use App Password, not regular password
```

#### SendGrid
```env
MAIL_HOST=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

#### Amazon SES
```env
MAIL_HOST=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USERNAME=your-ses-smtp-username
MAIL_PASSWORD=your-ses-smtp-password
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

#### Mailgun
```env
MAIL_HOST=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@your-domain.mailgun.org
MAIL_PASSWORD=your-mailgun-smtp-password
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Run database migrations:
```bash
alembic upgrade head
```

## Usage

### Basic Usage with Dependency Injection

```python
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.services.interfaces.email_service_interface import IEmailService

router = APIRouter()

@router.post("/send-notification")
@inject
async def send_notification(
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    await email_service.send_email_async(
        subject="Important Notification",
        body="<h1>Alert</h1><p>This is an important message.</p>",
        receivers={"user@example.com": "John Doe"}
    )
    return {"status": "sent"}
```

### Send Simple Email

```python
await email_service.send_email_async(
    subject="Welcome!",
    body="<h1>Welcome to our platform</h1>",
    receivers={"user@example.com": "John Doe"}
)
```

### Send Email with CC and BCC

```python
await email_service.send_email_async(
    subject="Team Update",
    body="<p>Here's the latest team update...</p>",
    receivers={
        "john@example.com": "John Doe",
        "jane@example.com": "Jane Smith"
    },
    cc_list={
        "manager@example.com": "Team Manager"
    },
    bcc_list={
        "admin@example.com": None  # No display name
    }
)
```

### Send Email with Attachments

```python
await email_service.send_email_async(
    subject="Monthly Report",
    body="<p>Please find the attached report.</p>",
    receivers={"user@example.com": "John Doe"},
    attachments=[
        "/path/to/report.pdf",
        "/path/to/chart.png"
    ]
)
```

### Complete Example

```python
from app.services.interfaces.email_service_interface import IEmailService
from dependency_injector.wiring import inject, Provide
from app.core.container import Container

@inject
async def send_user_registration_email(
    user_email: str,
    user_name: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """Send welcome email after user registration."""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #333;">Welcome {user_name}!</h1>
            <p>Thank you for registering with our platform.</p>
            <p>Click the button below to verify your email:</p>
            <a href="https://yourapp.com/verify" 
               style="display: inline-block; padding: 10px 20px; 
                      background-color: #007bff; color: white; 
                      text-decoration: none; border-radius: 5px;">
                Verify Email
            </a>
            <p style="margin-top: 20px; color: #666; font-size: 12px;">
                If you didn't create this account, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    await email_service.send_email_async(
        subject="Welcome - Please Verify Your Email",
        body=html_body,
        receivers={user_email: user_name}
    )
```

## Email Logger Model

The `EmailLogger` model tracks all email sending attempts:

```python
class EmailLogger(Base, AuditableEntity):
    id: UUID                    # Unique identifier
    from_email: str            # Sender email address
    subject: str               # Email subject
    body: str                  # Email body (HTML)
    to: str                    # JSON array of TO recipients
    cc: str                    # JSON array of CC recipients
    bcc: str                   # JSON array of BCC recipients
    total_email_sent: int      # Number of emails sent
    status: EmailStatus        # SUCCESS or FAILED
    error_message: str         # Error details if failed
    # + AuditableEntity fields (created_on, created_by, etc.)
```

### Email Statuses

- `SUCCESS`: Email sent successfully
- `FAILED`: Email sending failed (check error_message)

## Querying Email Logs

```python
from app.repositories.interfaces.email_log_repository_interface import IEmailLogRepository

# Get all email logs
logs = await email_log_repository.get_all(skip=0, limit=50)

# Get specific log by ID
log = await email_log_repository.get_by_id(email_id)

# Check log status
if log.status == EmailStatus.SUCCESS:
    print(f"Email sent to {log.total_email_sent} recipients")
else:
    print(f"Email failed: {log.error_message}")
```

## Error Handling

The service handles various error scenarios:

1. **Invalid Email Addresses**: Automatically filtered out
2. **No Valid Recipients**: Email not sent, logged as failed
3. **Attachment Not Found**: Logged as warning, email still sent
4. **SMTP Errors**: Logged with full error details
5. **Network Issues**: Caught and logged

All errors are logged to:
- Python logger (with stack traces)
- Database EmailLogger table

## Testing

### Test Configuration

For testing, use a test SMTP server:

```env
MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_USE_TLS=True
```

### Example Test

```python
import pytest
from app.services.email_service import EmailService

@pytest.mark.asyncio
async def test_send_email(db_session):
    email_service = EmailService(db=db_session)
    
    await email_service.send_email_async(
        subject="Test Email",
        body="<p>This is a test</p>",
        receivers={"test@example.com": "Test User"}
    )
    
    # Verify email log created
    logs = await db_session.execute(
        select(EmailLogger).order_by(EmailLogger.created_on.desc())
    )
    log = logs.scalars().first()
    
    assert log is not None
    assert log.status == EmailStatus.SUCCESS
    assert log.subject == "Test Email"
```

## API Endpoints

The example endpoint in `app/api/endpoints/v1/email.py` demonstrates usage:

### POST /api/v1/email/send

Send a custom email.

**Request:**
```json
{
    "subject": "Hello",
    "body": "<h1>Hello World</h1>",
    "to_emails": {
        "user@example.com": "John Doe"
    },
    "cc_emails": {
        "manager@example.com": "Manager"
    },
    "attachments": ["/path/to/file.pdf"]
}
```

**Response:**
```json
{
    "message": "Email sent successfully",
    "status": "success"
}
```

### POST /api/v1/email/send-welcome

Send a pre-formatted welcome email.

**Request:**
```json
{
    "user_email": "newuser@example.com",
    "user_name": "John Doe"
}
```

## Security Considerations

1. **Email Validation**: All email addresses are validated using regex
2. **BCC Privacy**: BCC recipients are never exposed in email headers
3. **Credentials**: Store SMTP credentials in environment variables
4. **Rate Limiting**: Consider adding rate limiting to prevent abuse
5. **Sanitization**: Always sanitize user input in email bodies

## Performance

- Async operations prevent blocking
- Database logging is non-blocking
- Attachment reading is optimized
- Consider background tasks for bulk emails

## Troubleshooting

### Common Issues

1. **Gmail "Less Secure Apps"**
   - Use App Password instead of regular password
   - Enable 2FA and generate App Password

2. **Connection Timeout**
   - Check firewall settings
   - Verify SMTP host and port
   - Try different port (587 vs 465)

3. **Authentication Failed**
   - Verify username and password
   - Check if account is locked
   - Ensure credentials are correct in .env file

4. **Email Not Received**
   - Check spam folder
   - Verify recipient email address
   - Check EmailLogger table for errors

## Best Practices

1. **Use HTML Templates**: Store email templates separately
2. **Background Tasks**: Use Celery/RQ for bulk emails
3. **Testing**: Always test with Mailtrap or similar service first
4. **Monitoring**: Monitor EmailLogger for failed emails
5. **Retry Logic**: Implement retry for transient failures
6. **Queue System**: Use message queue for high-volume scenarios

## Migration

Run the email logger migration:

```bash
alembic upgrade head
```

This creates the `identity.email_logs` table.

## Dependencies

- `aiosmtplib`: Async SMTP client
- `SQLAlchemy`: ORM for email logging
- `Pydantic`: Settings management
- `FastAPI`: Web framework
- `dependency-injector`: Dependency injection
