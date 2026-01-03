import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database.base import Base
from app.core.database.schema import DbSchemas
from app.models.auditable_entity import AuditableEntity

from sqlalchemy import UniqueConstraint

class UserRole(Base, AuditableEntity):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        {"schema": DbSchemas.identity},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DbSchemas.identity}.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DbSchemas.identity}.roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
