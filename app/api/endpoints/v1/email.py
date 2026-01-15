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


class WelcomeEmailRequest(BaseModel):
    """Request model for sending welcome emails."""
    user_email: EmailStr
    user_name: str


@router.post("/send-welcome", status_code=status.HTTP_200_OK)
@inject
async def send_welcome_email(
    request: WelcomeEmailRequest,
    email_service: IEmailService = Depends(Provide[Container.email_service])
) -> dict:
    """
    Send a welcome email to a new user.
    
    This is an example of how to use the email service in a real-world scenario,
    such as sending a welcome email after user registration.
    """
    try:
        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Our Platform!</h1>
                </div>
                <div class="content">
                    <h2>Hello {request.user_name},</h2>
                    <p>Thank you for joining our platform. We're excited to have you on board!</p>
                    <p>Here are some things you can do to get started:</p>
                    <ul>
                        <li>Complete your profile</li>
                        <li>Explore our features</li>
                        <li>Connect with other users</li>
                    </ul>
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 Your Company. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await email_service.send_email_async(
            subject="Welcome to Our Platform!",
            body=html_body,
            receivers={request.user_email: request.user_name}
        )
        
        return {
            "message": f"Welcome email sent to {request.user_email}",
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send welcome email: {str(e)}"
        )
