import uuid
from app.models.types import GUID
from sqlalchemy import Column, String, Text, Integer

from app.core.database.base import Base
from app.core.database.schema import DbSchemas
from app.models.auditable_entity import AuditableEntity
from app.models.enums import EmailStatus
from app.models.types import EmailStatusType


class EmailLogger(Base, AuditableEntity):
    __tablename__ = "email_logs"
    __table_args__ = {"schema": DbSchemas.logger}

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    from_email = Column(String(256), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    to = Column(Text, nullable=True)  # Stored as JSON string
    cc = Column(Text, nullable=True)  # Stored as JSON string
    bcc = Column(Text, nullable=True)  # Stored as JSON string
    total_email_sent = Column(Integer, nullable=False, default=0)
    status = Column(EmailStatusType, nullable=False, default=EmailStatus.FAILED)
    error_message = Column(Text, nullable=True)
