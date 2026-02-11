from typing import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.core.config import settings
from app.core.constants.validation import EMAIL_REGEX, validate_password_with_policy


class ResetPasswordRequest(BaseModel):
    email: str = Field(description="Email address associated with the account")
    verification_code: str = Field(description="Verification code sent to email")
    new_password: Annotated[str, Field(description="New password must be at least 8 characters")]
    confirm_password: Annotated[str, Field(description="Confirm new password")]

    @field_validator("new_password")
    def check_new_password_length(cls, value: str):
        return validate_password_with_policy(value, min_length=settings.PASSWORD_MIN_LENGTH, field_name="new_password")

    @field_validator("confirm_password")
    def check_confirm_password_length(cls, value: str):
        return validate_password_with_policy(value, min_length=settings.PASSWORD_MIN_LENGTH, field_name="confirm_password")

    @field_validator("email")
    def check_email_format(cls, value):
        if not EMAIL_REGEX.match(value):
            raise PydanticCustomError(
                "invalid_email_format",
                "Email must be a valid email address!"
            )
        return value

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise PydanticCustomError(
                "passwords_mismatch",
                "New password and confirm password do not match!"
            )
        return self
