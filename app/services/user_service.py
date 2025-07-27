import uuid
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_name(self, user_id: uuid) -> str:
        user =  await self.user_repository.get_user_by_id(user_id)
        if user:
            return user.username
        else:
            raise ValueError("User not found!")
