import uuid
from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.schema.response.user import UserResponse
from app.services.interfaces import IUserService


class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        user =  await self.user_repository.get_by_id_with_roles(user_id)

        for user_role in user.roles:
            print("Role:", user_role.role.normalized_name)

        if user:
            return UserResponse(full_name=user.full_name, email=user.email, id=user.id)
        else:
            raise ValueError("User not found!")
