from pydantic import BaseModel, Field


class ConfirmEmailRequest(BaseModel):
    email: str = Field(description="Email address to confirm")
    verification_code: str = Field(description="Verification code sent to email")
