import uuid
from app.repositories.user_repository import UserRepository
from app.schema.response.user import UserResponse


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        user =  await self.user_repository.get_by_id_with_roles(user_id)

        for role in user.roles:
            print("Role:", role.role.normalized_name)

        if user:
            return UserResponse(full_name=user.full_name, email=user.email, id=user.id)
        else:
            raise ValueError("User not found!")
