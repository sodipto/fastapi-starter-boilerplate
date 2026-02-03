from pydantic import BaseModel, Field


class UserStatusRequest(BaseModel):
    """Request schema for updating user status."""
    
    is_active: bool = Field(description="Whether the user account is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_active": True
            }
        }
