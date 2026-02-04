from pydantic import BaseModel, Field


class ResendConfirmationRequest(BaseModel):
    email: str = Field(description="Email address to resend confirmation to")
