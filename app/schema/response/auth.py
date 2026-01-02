from pydantic import BaseModel

from app.schema.response.user import UserResponse

class TokenResponse(BaseModel):
    type: str
    access_token: str
    refresh_token: str

class AuthResponse(BaseModel):
    tokenInfo: TokenResponse
    userInfo: UserResponse