
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from app.core.constants.validation import EMAIL_REGEX, validate_password_with_policy
from app.core.config import settings


class LoginRequest(BaseModel):
    email: str
    password: Annotated[str, Field(description="Password must be at least 8 characters")]

    @field_validator("email")
    def check_email_format(cls, value):
        if not EMAIL_REGEX.match(value):
            raise PydanticCustomError(
                "invalid_email_format",
                "Email must be a valid email address!"
            )
        return value
    
    @field_validator("password")
    def check_password(cls, v: str) -> str:
        return validate_password_with_policy(
            v, min_length=settings.PASSWORD_MIN_LENGTH, field_name="password"
        )
