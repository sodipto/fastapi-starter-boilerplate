from abc import ABC, abstractmethod


class IEmailService(ABC):
    """Interface for email service."""

    @abstractmethod
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
        Send an email asynchronously.
        
        Args:
            subject: Email subject
            body: Email body (HTML supported)
            receivers: Dictionary of email addresses with optional display names {email: name or None}
            cc_list: Optional dictionary of CC recipients {email: name or None}
            bcc_list: Optional dictionary of BCC recipients {email: name or None}
            attachments: Optional list of file paths to attach
        """
        pass
