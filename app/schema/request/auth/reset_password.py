from typing import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.core.constants.validation import EMAIL_REGEX


class ResetPasswordRequest(BaseModel):
    email: str = Field(description="Email address associated with the account")
    verification_code: str = Field(description="Verification code sent to email")
    new_password: Annotated[str, Field(min_length=8, description="New password (minimum 8 characters)")]
    confirm_password: Annotated[str, Field(min_length=8, description="Confirm new password")]

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
