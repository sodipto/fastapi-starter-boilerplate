import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Text, Integer, Enum as SQLEnum
import enum

from app.core.database.base import Base
from app.core.database.schema import DbSchemas
from app.models.auditable_entity import AuditableEntity


class EmailStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class EmailLogger(Base, AuditableEntity):
    __tablename__ = "email_logs"
    __table_args__ = {"schema": DbSchemas.identity}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    to = Column(Text, nullable=True)  # Stored as JSON string
    cc = Column(Text, nullable=True)  # Stored as JSON string
    bcc = Column(Text, nullable=True)  # Stored as JSON string
    total_email_sent = Column(Integer, nullable=False, default=0)
    status = Column(SQLEnum(EmailStatus), nullable=False, default=EmailStatus.FAILED)
    error_message = Column(Text, nullable=True)
