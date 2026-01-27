"""
Cross-database compatible GUID/UUID type.
Works with PostgreSQL, MySQL, and SQL Server.
"""
import uuid
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type, SQL Server's UNIQUEIDENTIFIER,
    or CHAR(36) for other databases, storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        elif dialect.name == 'mssql':
            return dialect.type_descriptor(UNIQUEIDENTIFIER())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value) if not isinstance(value, uuid.UUID) else value
        elif dialect.name == 'mssql':
            return str(value) if not isinstance(value, uuid.UUID) else value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value
