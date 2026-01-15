from abc import ABC, abstractmethod
from typing import List
import uuid

from app.models.email_logger import EmailLogger


class IEmailLogRepository(ABC):
    """Interface for email log repository."""

    @abstractmethod
    async def create(self, email_log: EmailLogger) -> EmailLogger:
        """Create a new email log entry."""
        pass

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> EmailLogger | None:
        """Get email log by id."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 20) -> List[EmailLogger]:
        """Get all email logs with pagination."""
        pass
