from typing import Annotated
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from app.core.constants.validation import EMAIL_REGEX, validate_password_with_policy
from app.core.config import settings


class SignupRequest(BaseModel):
    email: str = Field(description="User email address")
    full_name: Annotated[str, Field(min_length=1, max_length=100, description="Full name of the user")]
    phone_number: str | None = Field(None, description="Phone number (optional)")
    password: Annotated[str, Field(min_length=8, description="Password must be at least 8 characters")]
    confirm_password: Annotated[str, Field(min_length=8, description="Confirm password must be at least 8 characters")]

    @field_validator("email")
    def check_email_format(cls, value: str):
        if not EMAIL_REGEX.match(value):
            raise PydanticCustomError(
                "invalid_email_format",
                "Email must be a valid email address!"
            )
        return value

    @field_validator("password")
    def check_password_length(cls, value: str):
        return validate_password_with_policy(value, min_length=settings.PASSWORD_MIN_LENGTH, field_name="password")
        

    @field_validator("confirm_password")
    def check_confirm_password_length(cls, value: str):
        return validate_password_with_policy(value, min_length=settings.PASSWORD_MIN_LENGTH, field_name="confirm_password")

    def model_validate(self):
        # Ensure passwords match
        if self.password != self.confirm_password:
            raise PydanticCustomError(
                "passwords_mismatch",
                "New password and confirm password do not match!"
            )
        return self
