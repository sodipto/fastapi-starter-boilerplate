from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class AuditableEntity:
    created_by = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    created_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_modified_by = Column(UUID(as_uuid=True), nullable=True)
    last_modified_on = Column(DateTime, nullable=True)
    deleted_on = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)