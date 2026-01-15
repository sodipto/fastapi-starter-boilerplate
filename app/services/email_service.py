import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from pathlib import Path
import re
import aiosmtplib
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.interfaces.email_service_interface import IEmailService
from app.core.config import settings
from app.models.email_logger import EmailLogger, EmailStatus


logger = logging.getLogger(__name__)


class EmailService(IEmailService):
    """Email service implementation using aiosmtplib."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.host = settings.MAIL_HOST
        self.port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.from_email = settings.MAIL_FROM_EMAIL
        self.from_name = settings.MAIL_FROM_NAME
        self.use_tls = settings.MAIL_USE_TLS
        self.use_ssl = settings.MAIL_USE_SSL

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _filter_valid_emails(self, email_dict: dict[str, str | None] | None) -> dict[str, str | None]:
        """Filter and return only valid email addresses."""
        if not email_dict:
            return {}
        return {email: name for email, name in email_dict.items() if self.validate_email(email)}

    def _format_email_addresses(self, email_dict: dict[str, str | None]) -> list[str]:
        """Format email addresses with optional display names."""
        formatted = []
        for email, name in email_dict.items():
            if name:
                formatted.append(formataddr((name, email)))
            else:
                formatted.append(email)
        return formatted

    async def send_email_async(
        self,
        subject: str,
        body: str,
        receivers: dict[str, str | None],
        cc_list: dict[str, str | None] | None = None,
        bcc_list: dict[str, str | None] | None = None,
        attachments: list[str] | None = None
    ) -> None:
        """
        Send an email asynchronously with logging.
        
        Args:
            subject: Email subject
            body: Email body (HTML supported)
            receivers: Dictionary of email addresses with optional display names
            cc_list: Optional dictionary of CC recipients
            bcc_list: Optional dictionary of BCC recipients
            attachments: Optional list of file paths to attach
        """
        # Validate and filter email addresses
        valid_receivers = self._filter_valid_emails(receivers)
        valid_cc = self._filter_valid_emails(cc_list)
        valid_bcc = self._filter_valid_emails(bcc_list)

        # Initialize email log
        email_log = EmailLogger(
            from_email=self.from_email,
            subject=subject,
            body=body,
            to=json.dumps(list(valid_receivers.keys())) if valid_receivers else None,
            cc=json.dumps(list(valid_cc.keys())) if valid_cc else None,
            bcc=json.dumps(list(valid_bcc.keys())) if valid_bcc else None,
            total_email_sent=0,
            status=EmailStatus.FAILED
        )

        try:
            # Check if there are any valid recipients
            total_recipients = len(valid_receivers) + len(valid_cc) + len(valid_bcc)
            if total_recipients == 0:
                error_msg = "No valid recipients found. Email not sent."
                logger.warning(error_msg)
                email_log.error_message = error_msg
                self.db.add(email_log)
                await self.db.commit()
                return

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = formataddr((self.from_name, self.from_email))
            
            # Add recipients
            if valid_receivers:
                message["To"] = ", ".join(self._format_email_addresses(valid_receivers))
            if valid_cc:
                message["Cc"] = ", ".join(self._format_email_addresses(valid_cc))
            # BCC is not added to headers for privacy

            # Add HTML body
            html_part = MIMEText(body, "html", "utf-8")
            message.attach(html_part)

            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    await self._add_attachment(message, file_path)

            # Collect all recipient emails for sending
            all_recipients = (
                list(valid_receivers.keys()) +
                list(valid_cc.keys()) +
                list(valid_bcc.keys())
            )

            # Send email via SMTP
            await self._send_smtp(message, all_recipients)

            # Update log with success
            email_log.status = EmailStatus.SUCCESS
            email_log.total_email_sent = len(all_recipients)
            logger.info(f"Email sent successfully to {len(all_recipients)} recipients: {subject}")

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg, exc_info=True)
            email_log.error_message = error_msg
            email_log.status = EmailStatus.FAILED

        finally:
            # Save email log to database
            self.db.add(email_log)
            await self.db.commit()

    async def _add_attachment(self, message: MIMEMultipart, file_path: str) -> None:
        """Add a file attachment to the email message."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Attachment file not found: {file_path}")
                return

            with open(path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {path.name}",
            )
            message.attach(part)
            logger.debug(f"Added attachment: {path.name}")

        except Exception as e:
            logger.error(f"Failed to add attachment {file_path}: {str(e)}")

    async def _send_smtp(self, message: MIMEMultipart, recipients: list[str]) -> None:
        """Send the email via SMTP."""
        smtp_kwargs = {
            "hostname": self.host,
            "port": self.port,
        }

        # Configure TLS/SSL
        if self.use_ssl:
            smtp_kwargs["use_tls"] = True
        elif self.use_tls:
            smtp_kwargs["start_tls"] = True

        # Add authentication if credentials provided
        if self.username and self.password:
            smtp_kwargs["username"] = self.username
            smtp_kwargs["password"] = self.password

        # Send email
        async with aiosmtplib.SMTP(**smtp_kwargs) as smtp:
            await smtp.send_message(message, recipients=recipients)
