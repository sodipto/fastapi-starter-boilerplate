from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, JSON
from app.core.database.base import Base
from app.core.database.schema import DbSchemas


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": DbSchemas.logger}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    type = Column(String(32), nullable=False)  # Insert, Update, Delete
    table_name = Column(String(255), nullable=True)
    date_time = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    affected_columns = Column(JSON, nullable=True)
    primary_key = Column(JSON, nullable=True)
