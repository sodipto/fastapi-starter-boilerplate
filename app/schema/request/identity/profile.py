from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import Annotated, Optional

from app.core.constants.validation import EMAIL_REGEX, ALPHANUMERIC_REGEX


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
    current_password: Annotated[str, Field(description="Current password")]
    new_password: Annotated[str, Field(description="New password must be between 6 and 8 characters")]
    confirm_password: Annotated[str, Field(description="Password confirmation")]
    
    @field_validator("current_password", "new_password", "confirm_password")
    @classmethod
    def check_password_length(cls, v: str) -> str:
        if not (6 <= len(v) <= 8):
            raise PydanticCustomError(
                "password_length",
                "Password must be between 6 and 8 characters!"
            )
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldPass1",
                "new_password": "newPass1",
                "confirm_password": "newPass1"
            }
        }
