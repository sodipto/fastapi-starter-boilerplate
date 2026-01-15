"""
Email Service Usage Examples

This file contains practical examples of how to use the EmailService
in different scenarios within your FastAPI application.
"""

from app.services.interfaces.email_service_interface import IEmailService
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
from fastapi import Depends


# Example 1: User Registration Email
@inject
async def send_registration_email(
    user_email: str,
    user_name: str,
    verification_token: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """Send verification email after user registration."""
    
    verification_link = f"https://yourapp.com/verify?token={verification_token}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                font-family: Arial, sans-serif;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                text-align: center;
                color: white;
            }}
            .content {{
                padding: 30px;
                background-color: #f8f9fa;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #6c757d;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Welcome to Our Platform!</h1>
            </div>
            <div class="content">
                <h2>Hello {user_name},</h2>
                <p>Thank you for creating an account. Please verify your email address to get started.</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_link}</p>
                <p>This link will expire in 24 hours.</p>
            </div>
            <div class="footer">
                <p>If you didn't create this account, please ignore this email.</p>
                <p>&copy; 2026 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    await email_service.send_email_async(
        subject="Verify Your Email Address",
        body=html_body,
        receivers={user_email: user_name}
    )


# Example 2: Password Reset Email
@inject
async def send_password_reset_email(
    user_email: str,
    user_name: str,
    reset_token: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """Send password reset email."""
    
    reset_link = f"https://yourapp.com/reset-password?token={reset_token}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Password Reset Request</h2>
            <p>Hello {user_name},</p>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #dc3545; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                For security reasons, never share this link with anyone.
            </p>
        </div>
    </body>
    </html>
    """
    
    await email_service.send_email_async(
        subject="Password Reset Request",
        body=html_body,
        receivers={user_email: user_name}
    )


# Example 3: Order Confirmation Email with Attachment
@inject
async def send_order_confirmation_email(
    customer_email: str,
    customer_name: str,
    order_id: str,
    order_total: float,
    invoice_path: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """Send order confirmation with invoice attachment."""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #28a745;">Order Confirmed!</h1>
            <p>Dear {customer_name},</p>
            <p>Thank you for your order. Your order has been confirmed and is being processed.</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Order Details</h3>
                <p><strong>Order ID:</strong> {order_id}</p>
                <p><strong>Total:</strong> ${order_total:.2f}</p>
                <p><strong>Status:</strong> Processing</p>
            </div>
            
            <p>Your invoice is attached to this email for your records.</p>
            <p>We'll send you another email when your order ships.</p>
            
            <p style="margin-top: 30px;">
                Best regards,<br>
                The Sales Team
            </p>
        </div>
    </body>
    </html>
    """
    
    await email_service.send_email_async(
        subject=f"Order Confirmation - #{order_id}",
        body=html_body,
        receivers={customer_email: customer_name},
        attachments=[invoice_path]
    )


# Example 4: Team Notification with CC
@inject
async def send_team_notification(
    team_emails: dict[str, str],
    manager_email: str,
    manager_name: str,
    notification_title: str,
    notification_message: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """Send notification to team with manager in CC."""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #ffc107; padding: 15px; border-radius: 5px;">
                <h2 style="margin: 0; color: #333;">📢 {notification_title}</h2>
            </div>
            <div style="padding: 20px; background-color: #f8f9fa; margin-top: 20px; border-radius: 5px;">
                <p>{notification_message}</p>
            </div>
            <p style="margin-top: 20px; color: #666; font-size: 12px;">
                This is an automated notification. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    await email_service.send_email_async(
        subject=notification_title,
        body=html_body,
        receivers=team_emails,
        cc_list={manager_email: manager_name}
    )


# Example 5: Monthly Newsletter with Multiple Recipients
@inject
async def send_monthly_newsletter(
    subscribers: dict[str, str],
    newsletter_html: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """
    Send monthly newsletter to all subscribers.
    
    Note: For large lists, consider using a background task queue like Celery
    or sending in batches to avoid timeout issues.
    """
    
    await email_service.send_email_async(
        subject="Monthly Newsletter - January 2026",
        body=newsletter_html,
        receivers=subscribers,
        # Use BCC to hide subscriber emails from each other
        bcc_list=subscribers
    )


# Example 6: Support Ticket Notification
@inject
async def send_support_ticket_notification(
    customer_email: str,
    customer_name: str,
    ticket_id: str,
    support_team_email: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """Send support ticket confirmation to customer with support team in BCC."""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #007bff;">Support Ticket Created</h2>
            <p>Hello {customer_name},</p>
            <p>We've received your support request and have created a ticket for you.</p>
            
            <div style="background-color: #e7f3ff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                <p style="margin: 0;"><strong>Ticket ID:</strong> {ticket_id}</p>
            </div>
            
            <p>Our support team will review your request and respond within 24 hours.</p>
            <p>You can track the status of your ticket by replying to this email or visiting our support portal.</p>
            
            <p style="margin-top: 30px;">
                Thank you,<br>
                Support Team
            </p>
        </div>
    </body>
    </html>
    """
    
    await email_service.send_email_async(
        subject=f"Support Ticket #{ticket_id} Created",
        body=html_body,
        receivers={customer_email: customer_name},
        bcc_list={support_team_email: "Support Team"}
    )


# Example 7: Error/Exception Notification to Admins
@inject
async def send_error_notification_to_admins(
    admin_emails: dict[str, str],
    error_type: str,
    error_message: str,
    stack_trace: str,
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """Send critical error notification to administrators."""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Courier New', monospace;">
        <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #dc3545; color: white; padding: 15px; border-radius: 5px;">
                <h2 style="margin: 0;">🚨 Application Error Alert</h2>
            </div>
            
            <div style="margin-top: 20px; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
                <h3>Error Type:</h3>
                <p style="color: #dc3545; font-weight: bold;">{error_type}</p>
                
                <h3>Error Message:</h3>
                <p style="background-color: #fff; padding: 10px; border-left: 3px solid #dc3545;">
                    {error_message}
                </p>
                
                <h3>Stack Trace:</h3>
                <pre style="background-color: #fff; padding: 15px; overflow-x: auto; border: 1px solid #ddd;">
{stack_trace}
                </pre>
            </div>
            
            <p style="margin-top: 20px; color: #666; font-size: 12px;">
                This is an automated error notification. Please investigate immediately.
            </p>
        </div>
    </body>
    </html>
    """
    
    await email_service.send_email_async(
        subject=f"🚨 CRITICAL ERROR: {error_type}",
        body=html_body,
        receivers=admin_emails
    )


# Example 8: Batch Email Sending (with rate limiting consideration)
@inject
async def send_batch_emails(
    recipients: list[tuple[str, str, str]],  # [(email, name, custom_message), ...]
    email_service: IEmailService = Depends(Provide[Container.email_service])
):
    """
    Send personalized emails to multiple recipients.
    
    Args:
        recipients: List of tuples containing (email, name, custom_message)
    
    Note: Consider rate limiting and using background tasks for large batches.
    """
    import asyncio
    
    for email, name, custom_message in recipients:
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Hello {name},</h2>
            <p>{custom_message}</p>
            <p>Best regards,<br>Your Team</p>
        </body>
        </html>
        """
        
        await email_service.send_email_async(
            subject="Personalized Message",
            body=html_body,
            receivers={email: name}
        )
        
        # Add small delay to avoid overwhelming SMTP server
        await asyncio.sleep(0.5)
