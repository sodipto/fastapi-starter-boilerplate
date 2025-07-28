import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String

from app.core.database.base import Base

class User(Base):
    __tablename__ = "Users"
    __table_args__ = {"schema": "Identity"}

    Id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    FullName = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
