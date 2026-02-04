from app.core.database.session import get_db
from app.services import UserService, AuthService, EmailService, SchedulerService
from app.services.profile_service import ProfileService
from app.services.token_service import TokenService
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.services.AWS_s3_document_storage_service import AwsS3DocumentStorageService
from app.services.email_template_service import EmailTemplateService
from app.repositories import UserRepository, EmailLogRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
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
            "app.api.endpoints.v1.profile",
            "app.api.endpoints.v1.cache",
            "app.core.rbac.dependencies",  # RBAC permission dependencies
        ]
    )

    # Request-scoped AsyncSession
    db_session = providers.Resource(async_session)

    # Cache service - injected from app.state during startup
    cache_service = providers.Object(None)

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

    # RBAC: Permission repository for loading user permissions
    permission_repository = providers.Factory(
        PermissionRepository,
        db=db_session
    )

    token_service = providers.Singleton(
        TokenService
    )

    email_service = providers.Factory(
        EmailService,
        db=db_session
    )

    email_template_service = providers.Singleton(
        EmailTemplateService
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        role_repository=role_repository,
        email_service=email_service,
        email_template_service=email_template_service
    )

    profile_service = providers.Factory(
        ProfileService,
        user_repository=user_repository
    )

    role_service = providers.Factory(
        RoleService,
        role_repository=role_repository
    )

    # RBAC: Permission service with caching for authorization
    permission_service = providers.Factory(
        PermissionService,
        permission_repository=permission_repository,
        cache_service=cache_service
    )

    email_service = providers.Factory(
        EmailService,
        db=db_session
    )

    email_template_service = providers.Singleton(
        EmailTemplateService
    )

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        token_service=token_service,
        cache_service=cache_service,
        email_service=email_service,
        email_template_service=email_template_service
    )

    document_storage_service = providers.Singleton(
        AwsS3DocumentStorageService
    )

    scheduler_service = providers.Singleton(
        SchedulerService
    )

