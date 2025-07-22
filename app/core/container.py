from app.services import*
from app.repositories import UserRepository

from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.user",
            "app.api.v1.endpoints.auth",
        ]
    )

    user_repository = providers.Factory(UserRepository)
    user_service = providers.Factory(
        UserService, user_repository=user_repository)
    auth_service = providers.Factory(
        AuthService, user_repository=user_repository)
