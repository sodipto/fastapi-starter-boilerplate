from app.core.database.session import get_db
from app.services import UserService, AuthService
from app.repositories import UserRepository
from dependency_injector import containers, providers
from app.core.database.session import async_session

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.v1.user",
            "app.api.endpoints.v1.auth",
        ]
    )

    # Provide AsyncSession instance via the get_db dependency function
    db_session = providers.Resource(async_session)
    # UserRepository receives an AsyncSession instance
    user_repository = providers.Factory(
        UserRepository,
        db=db_session
    )

    # Services receive UserRepository instances
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository
    )
