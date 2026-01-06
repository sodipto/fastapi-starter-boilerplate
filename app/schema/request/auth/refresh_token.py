from pydantic import BaseModel, Field


class TokenRefreshRequest(BaseModel):
    """
    Request model for refreshing access and refresh tokens.
    """
    access_token: str = Field(..., description="The current access token")
    refresh_token: str = Field(..., description="The current refresh token")
