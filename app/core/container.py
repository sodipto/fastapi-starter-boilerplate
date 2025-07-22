from app.services import UserService
from app.repositories import UserRepository

from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.user",
        ]
    )

    user_repository = providers.Factory(UserRepository)
    user_service = providers.Factory(
        UserService, user_repository=user_repository)
