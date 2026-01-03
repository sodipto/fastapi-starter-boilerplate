import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database.base import Base
from app.core.database.schema import DbSchemas
from app.models.auditable_entity import AuditableEntity

class Role(Base, AuditableEntity):
    __tablename__ = "roles"
    __table_args__ = {"schema": DbSchemas.identity}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False, index=True, unique=True)
    description = Column(String, nullable=True)
    is_system = Column(Boolean, nullable=False, default=False)

    role_claims = relationship(
        "RoleClaim",
        back_populates="role",
        cascade="all, delete-orphan"
    )
