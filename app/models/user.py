import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship


from app.core.database.base import Base
from app.core.database.schema import DbSchemas
from app.models.auditable_entity import AuditableEntity
from app.models.types import GUID

class User(Base, AuditableEntity):
    __tablename__ = "users"
    __table_args__ = {"schema": DbSchemas.identity}

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(256), unique=True, index=True, nullable=False)
    full_name = Column(String(256), nullable=False)
    password = Column(String(512), nullable=False)
    refresh_token = Column(String(512), nullable=True)
    refresh_token_expiry_time = Column(DateTime(timezone=True), nullable=True)

    roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )