import uuid
from sqlalchemy import Column, String, ForeignKey
from app.models.types import GUID
from sqlalchemy.orm import relationship

from app.core.database.base import Base
from app.core.database.schema import DbSchemas
from app.models.auditable_entity import AuditableEntity

class RoleClaim(Base, AuditableEntity):
    __tablename__ = "role_claims"
    __table_args__ = {"schema": DbSchemas.identity}

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    claim_type = Column(String(256), nullable=False)
    claim_name = Column(String(256), nullable=False)

    role_id = Column(
        GUID(),
        ForeignKey(f"{DbSchemas.identity}.roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role = relationship("Role", back_populates="role_claims")
