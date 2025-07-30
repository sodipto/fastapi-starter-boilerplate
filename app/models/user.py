import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String

from app.core.database.base import Base
from app.core.database.schema import DbSchemas

class User(Base):
    __tablename__ = "Users"
    __table_args__ = {"schema": DbSchemas.identity}

    Id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    Email = Column(String, unique=True, index=True, nullable=False)
    FullName = Column(String, nullable=False)
    Hashed_Password = Column(String, nullable=False)
