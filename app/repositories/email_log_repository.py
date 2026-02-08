from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.email_log_repository_interface import IEmailLogRepository
from app.models.email_logger import EmailLogger


class EmailLogRepository(BaseRepository[EmailLogger], IEmailLogRepository):
    """Repository for email log operations."""

    def __init__(self, db_factory):
        super().__init__(db_factory, EmailLogger)
