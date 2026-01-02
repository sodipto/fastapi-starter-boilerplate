from typing import Dict, Optional
from app.repositories.user_repository import UserRepository
from app.utils.auth_utils import verify_password, create_access_token
from app.utils.exception_utils import NotFoundException, UnauthorizedException
from app.schema.response.auth import AuthResponse, TokenResponse
from app.schema.response.user import UserResponse


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> AuthResponse:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundException(
                key="email",
                message=f"User not found with this email=> {email}",
            )
        if not verify_password(password, user.password):
            raise UnauthorizedException(
                message="Incorrect username or password!",
            )

        access_token = create_access_token(
            data={
                "id": str(user.id),
                "name": user.full_name,
                "email": user.email,
            }
        )

        return AuthResponse(
            tokenInfo=TokenResponse(
                type="bearer",
                access_token=access_token,
                refresh_token="",
            ),
            userInfo=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
            ),
        )
