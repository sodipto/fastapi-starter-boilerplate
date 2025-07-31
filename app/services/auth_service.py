from typing import Dict, Optional
from fastapi import HTTPException,status
from app.repositories.user_repository import UserRepository
from app.utils.auth_utils import verify_password
from app.utils.exception_utils import NotFoundException, UnauthorizedException


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise NotFoundException(
                key="email",
                message=f"User not found with this email=> {email}",
            )
        if not verify_password(password, user.Hashed_Password):
            raise UnauthorizedException(
                message="Incorrect username or password!",
            )

        return user
