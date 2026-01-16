from sqlalchemy import String, TypeDecorator
from app.models.enums import EmailStatus


class EmailStatusType(TypeDecorator):
    impl = String(20)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, EmailStatus):
            return value.value
        if value not in EmailStatus._value2member_map_:
            raise ValueError(f"Invalid EmailStatus: {value}")
        return value
