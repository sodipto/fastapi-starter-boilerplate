from sqlalchemy import Column, DateTime, Boolean, event
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone

class AuditableEntity:
    created_by = Column(UUID(as_uuid=True), nullable=False, default=lambda: uuid.UUID(int=0))
    created_on = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_modified_by = Column(UUID(as_uuid=True), nullable=False, default=lambda: uuid.UUID(int=0))
    last_modified_on = Column(DateTime(timezone=True), nullable=True, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_on = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)

# Automatically set timestamps for AuditableEntity
@event.listens_for(AuditableEntity, "before_insert")
def set_created_on_and_last_modified_on(mapper, connection, target):
    target.created_on = datetime.now(timezone.utc)
    target.last_modified_on = datetime.now(timezone.utc)

@event.listens_for(AuditableEntity, "before_update")
def set_last_modified_on(mapper, connection, target):
    target.last_modified_on = datetime.now(timezone.utc)