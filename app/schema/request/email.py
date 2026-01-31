from pydantic import BaseModel, EmailStr


class SendEmailRequest(BaseModel):
    """Request model for sending emails."""
    subject: str
    body: str
    to_emails: dict[EmailStr, str | None]
    cc_emails: dict[EmailStr, str | None] | None = None
    bcc_emails: dict[EmailStr, str | None] | None = None
    attachments: list[str] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "subject": "Welcome to Our Platform",
                    "body": "<h1>Welcome!</h1><p>Thank you for joining us.</p>",
                    "to_emails": {
                        "user@example.com": "John Doe",
                        "another@example.com": None
                    },
                    "cc_emails": {
                        "manager@example.com": "Manager Name"
                    },
                    "bcc_emails": {
                        "admin@example.com": "Admin"
                    },
                    "attachments": [
                        "/path/to/file1.pdf",
                        "/path/to/file2.jpg"
                    ]
                }
            ]
        }
    }
