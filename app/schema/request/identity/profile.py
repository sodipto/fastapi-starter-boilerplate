from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from app.core.config import settings
from typing import Annotated, Optional

from app.core.constants.validation import EMAIL_REGEX, ALPHANUMERIC_REGEX, validate_password_with_policy


class UpdateProfileRequest(BaseModel):
    """Schema for updating user profile information."""
    full_name: Annotated[str, Field(min_length=1, max_length=256, description="User's full name")]
    phone_number: Annotated[str | None, Field(description="User's phone number")] = None
    
    @field_validator("full_name")
    @classmethod
    def check_full_name_format(cls, value: str) -> str:
        if not ALPHANUMERIC_REGEX.match(value):
            raise PydanticCustomError(
                "invalid_full_name_format",
                "Full name must contain only alphanumeric characters!"
            )
        return value
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "phone_number": "+1234567890"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password."""
    current_password: Annotated[str, Field(description="Current password must be at least 8 characters")]
    new_password: Annotated[str, Field(description="New password must be at least 8 characters")]
    confirm_password: Annotated[str, Field(description="Confirm new password must be at least 8 characters")]
    
    @field_validator("current_password")
    @classmethod
    def check_current_password(cls, v: str) -> str:
        return validate_password_with_policy(
            v, min_length=settings.PASSWORD_MIN_LENGTH, field_name="current_password"
        )

    @field_validator("new_password")
    @classmethod
    def check_new_password(cls, v: str) -> str:
        return validate_password_with_policy(
            v, min_length=settings.PASSWORD_MIN_LENGTH, field_name="new_password"
        )

    @field_validator("confirm_password")
    @classmethod
    def check_confirm_password(cls, v: str) -> str:
        return validate_password_with_policy(
            v, min_length=settings.PASSWORD_MIN_LENGTH, field_name="confirm_password"
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass1@",
                "new_password": "NewPass1@",
                "confirm_password": "NewPass1@"
            }
        }


class ChangeEmailRequest(BaseModel):
    """Schema for changing user email."""
    email: Annotated[str, Field(description="New email address")]

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v):
            raise PydanticCustomError("invalid_email_format", "Invalid email format")
        return v

    class Config:
        json_schema_extra = {
            "example": {"email": "new.email@example.com"}
        }
