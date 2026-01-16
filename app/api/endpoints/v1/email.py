"""
Example endpoint demonstrating email service usage.

This is a reference implementation showing how to use the EmailService
with dependency injection in FastAPI endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, EmailStr

from app.core.container import Container
from app.services.interfaces.email_service_interface import IEmailService


router = APIRouter(prefix="/email", tags=["Email"])


class SendEmailRequest(BaseModel):
    """Request model for sending emails."""
    subject: str
    body: str
    to_emails: dict[EmailStr, str | None]
    cc_emails: dict[EmailStr, str | None] | None = None
    bcc_emails: dict[EmailStr, str | None] | None = None
    attachments: list[str] | None = None


@router.post("/send", status_code=status.HTTP_200_OK)
@inject
async def send_email(
    request: SendEmailRequest,
    email_service: IEmailService = Depends(Provide[Container.email_service])
) -> dict:
    """
    Send an email.
    
    Example request body:
    ```json
    {
        "subject": "Welcome to Our Platform",
        "body": "<h1>Welcome!</h1><p>Thank you for joining us.</p>",
        "to_emails": {
            "user@example.com": "John Doe",
            "another@example.com": null
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
    ```
    """
    try:
        await email_service.send_email_async(
            subject=request.subject,
            body=request.body,
            receivers=request.to_emails,
            cc_list=request.cc_emails,
            bcc_list=request.bcc_emails,
            attachments=request.attachments
        )
        
        return {
            "message": "Email sent successfully",
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )