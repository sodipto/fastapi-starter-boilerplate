from datetime import datetime
from pydantic import BaseModel

from app.schema.response.user import UserResponse

class TokenResponse(BaseModel):
    type: str
    access_token: str
    access_token_expiry_time: datetime
    refresh_token: str
    refresh_token_expiry_time: datetime


class AuthResponse(BaseModel):
    tokenInfo: TokenResponse
    userInfo: UserResponse