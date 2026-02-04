# Email Service Guide

This document covers email configuration, template rendering, and sending emails in the application.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Email Templates](#email-templates)
- [Sending Emails](#sending-emails)
- [Email Logging](#email-logging)
- [Troubleshooting](#troubleshooting)

---

## Overview

The email system consists of two services:

| Service | Responsibility |
|---------|----------------|
| `EmailService` | SMTP connection and sending emails |
| `EmailTemplateService` | Loading and rendering Jinja2 templates |

---

## Configuration

Add these variables to your `.env` file:

```env
# SMTP Server
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=Your App Name

# Optional
EMAIL_USE_TLS=True
EMAIL_TIMEOUT=30
```

### Gmail Setup

1. Enable 2-Step Verification in your Google account
2. Generate an App Password:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Select "App passwords"
   - Generate a password for "Mail"
3. Use the generated password as `EMAIL_PASSWORD`

---

## Email Templates

Templates are stored in `app/templates/emails/` as Jinja2 HTML files.

### Available Templates

| Template | Purpose | Variables |
|----------|---------|-----------|
| `reset_password.html` | Password reset email | `user_name`, `reset_link`, `expire_minutes` |
| `confirm_email.html` | Email verification | `user_name`, `verification_code`, `frontend_url`, `expire_minutes` |

### Creating a Template

1. Create an HTML file in `app/templates/emails/`:

```html
<!-- app/templates/emails/welcome.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        .container { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .button { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Our App!</h1>
        </div>
        <div class="content">
            <p>Hello {{ user_name }},</p>
            <p>Thank you for signing up. We're excited to have you on board!</p>
            <p>
                <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
            </p>
        </div>
    </div>
</body>
</html>
```

2. Use the template in your service:

```python
body = await self._email_template_service.render(
    "welcome.html",
    {
        "user_name": user.full_name,
        "dashboard_url": f"{settings.FRONTEND_URL}/dashboard"
    }
)

await self._email_service.send_email(
    to_email=user.email,
    subject="Welcome to Our App!",
    body=body
)
```

---

## Sending Emails

### Using EmailService

The `EmailService` is available via dependency injection:

```python
from dependency_injector.wiring import Depends, Provide, inject
from app.core.container import Container
from app.services.interfaces.email_service_interface import IEmailService

@inject
async def send_notification(
    user_email: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    await email_service.send_email(
        to_email=user_email,
        subject="Notification",
        body="<p>You have a new notification.</p>"
    )
```

### EmailService Methods

```python
class IEmailService(ABC):
    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> bool:
        """Send an HTML email."""
        pass
```

### EmailTemplateService Methods

```python
class IEmailTemplateService(ABC):
    @abstractmethod
    async def render(
        self,
        template_name: str,
        context: dict
    ) -> str:
        """Render an email template with the given context."""
        pass
```

---

## Email Logging

All sent emails are logged to the `email_logs` table for auditing:

| Column | Description |
|--------|-------------|
| `id` | UUID primary key |
| `to_email` | Recipient address |
| `subject` | Email subject |
| `status` | `pending`, `sent`, `failed` |
| `error_message` | Error details if failed |
| `sent_at` | Timestamp when sent |
| `created_at` | Record creation time |

### Checking Email Logs

```python
email_logs = await email_log_repository.get_by_recipient(
    email="user@example.com",
    limit=10
)
```

---

## Troubleshooting

### Common Issues

#### "Authentication failed"

- Verify `EMAIL_USERNAME` and `EMAIL_PASSWORD`
- For Gmail, ensure you're using an App Password
- Check if "Less secure app access" is needed (not recommended)

#### "Connection timeout"

- Verify `EMAIL_HOST` and `EMAIL_PORT`
- Check firewall rules for outbound SMTP
- Try increasing `EMAIL_TIMEOUT`

#### "Template not found"

- Ensure the template file exists in `app/templates/emails/`
- Check the filename matches exactly (case-sensitive)

### Testing Email Configuration

```python
# Quick test in Python shell
import asyncio
from app.services.email_service import EmailService
from app.core.config import get_settings

async def test():
    settings = get_settings()
    service = EmailService(settings, None, None)
    result = await service.send_email(
        to_email="test@example.com",
        subject="Test",
        body="<p>Test email</p>"
    )
    print(f"Email sent: {result}")

asyncio.run(test())
```

---

## Best Practices

1. **Always use templates** for consistent branding
2. **Log all emails** for debugging and compliance
3. **Handle failures gracefully** - don't block user actions on email failures
4. **Use async sending** to avoid blocking the request
5. **Validate email addresses** before attempting to send
6. **Set reasonable timeouts** to prevent hanging requests
