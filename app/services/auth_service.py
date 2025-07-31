from typing import Dict, Optional
from fastapi import HTTPException,status
from app.repositories.user_repository import UserRepository
from app.utils.auth_utils import verify_password


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.Hashed_Password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password!",
        )
             
        return user
