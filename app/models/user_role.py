import uuid
from sqlalchemy import Column, ForeignKey
from app.models.types import GUID
from sqlalchemy.orm import relationship

from app.core.database.base import Base
from app.core.database.schema import DbSchemas
from app.models.auditable_entity import AuditableEntity

from sqlalchemy import UniqueConstraint, Index

class UserRole(Base, AuditableEntity):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        Index("ix_user_roles_role_id_user_id", "role_id", "user_id"),
        {"schema": DbSchemas.identity},
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        GUID(),
        ForeignKey(f"{DbSchemas.identity}.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role_id = Column(
        GUID(),
        ForeignKey(f"{DbSchemas.identity}.roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user = relationship("User")
    role = relationship("Role")
