from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from app.core.constants.validation import EMAIL_REGEX


class ForgotPasswordRequest(BaseModel):
    email: str = Field(description="Email address to send password reset code")

    @field_validator("email")
    def check_email_format(cls, value):
        if not EMAIL_REGEX.match(value):
            raise PydanticCustomError(
                "invalid_email_format",
                "Email must be a valid email address!"
            )
        return value
