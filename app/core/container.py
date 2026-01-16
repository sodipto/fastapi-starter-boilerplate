from app.core.database.session import get_db
from app.services import UserService, AuthService, EmailService
from app.services.token_service import TokenService
from app.services.role_service import RoleService
from app.services.AWS_s3_document_storage_service import AwsS3DocumentStorageService
from app.repositories import UserRepository, EmailLogRepository
from app.repositories.role_repository import RoleRepository
from dependency_injector import containers, providers
from app.core.database.session import async_session

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.endpoints.v1.user",
            "app.api.endpoints.v1.auth",
            "app.api.endpoints.v1.role",
            "app.api.endpoints.v1.email",
            "app.api.endpoints.v1.document",
        ]
    )

    # Request-scoped AsyncSession
    db_session = providers.Resource(async_session)

    user_repository = providers.Factory(
        UserRepository,
        db=db_session
    )

    role_repository = providers.Factory(
        RoleRepository,
        db=db_session
    )

    email_log_repository = providers.Factory(
        EmailLogRepository,
        db=db_session
    )

    token_service = providers.Singleton(
        TokenService
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )

    role_service = providers.Factory(
        RoleService,
        role_repository=role_repository
    )

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        token_service=token_service
    )

    email_service = providers.Factory(
        EmailService,
        db=db_session
    )

    file_storage_service = providers.Singleton(
        AwsS3DocumentStorageService
    )

