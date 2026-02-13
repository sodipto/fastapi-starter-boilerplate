from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# Initialize logging BEFORE importing any application modules
from app.core.config import settings
from app.core.logger import setup_logging, get_logger
setup_logging(
    log_level=settings.LOG_LEVEL,
    seq_server_url=settings.SEQ_SERVER_URL if settings.SEQ_ENABLED else None,
    seq_api_key=settings.SEQ_API_KEY if settings.SEQ_ENABLED and settings.SEQ_API_KEY else None
)

# Now import application modules (after logging is configured)
from app.core.container import Container
from app.api.endpoints.routes import routers as v1_routers
from app.core.database.migrate import run_pending_migrations
from app.core.middlewares.exception_middleware import CustomExceptionMiddleware
from app.core.middlewares.validation_exception_middleware import custom_validation_exception_middleware
from app.core.middlewares.rate_limit_middleware import RateLimitMiddleware
from app.core.open_api import custom_openapi
from app.core.seeders.application import ApplicationSeeder
from app.jobs import register_all_jobs
import app.core.audit  # registers audit event listeners


@asynccontextmanager
async def startup(app: FastAPI):
    """
    Application lifespan manager with declarative DI initialization.
    
    Key Design Improvements:
        1. No runtime DI overrides - all providers are declarative
        2. Container manages resource lifecycle (init/shutdown)
        3. Async resources (cache, db) properly initialized via Resource providers
        4. Testable: override container providers before init_resources()
    """
    _logger = get_logger(__name__)
    
    _logger.info("Starting up application...")
    
    # Database migrations (if enabled)
    if settings.DATABASE_ENABLED:
        run_pending_migrations()
        # Reconfigure logging after Alembic (which overrides logging config)
        setup_logging(
            log_level=settings.LOG_LEVEL,
            seq_server_url=settings.SEQ_SERVER_URL if settings.SEQ_ENABLED else None,
            seq_api_key=settings.SEQ_API_KEY if settings.SEQ_ENABLED and settings.SEQ_API_KEY else None
        )
        _logger = get_logger(__name__)  # Get fresh logger after reconfiguration
        try:
            await ApplicationSeeder().seed_data()
        except Exception as e:
            _logger.error(f"Seeding failed: {e}")
            raise SystemExit("Application startup aborted due to seeding failure.")
    
    # Initialize all container resources declaratively
    # This includes cache_service which is now a proper Resource provider
    await app.container.init_resources()
    _logger.info(f"Container resources initialized (cache type: {settings.CACHE_TYPE})")
    
    # Initialize and start the background scheduler
    scheduler_service = None
    if settings.BACKGROUND_JOBS_ENABLED:
        scheduler_service = app.container.scheduler_service()
        register_all_jobs(scheduler_service)
        scheduler_service.start()
        _logger.info("Background scheduler started.")
    
    _logger.info("Application startup complete.")
    
    yield

    # Shutdown
    _logger.info("Shutting down application...")
    
    # Shutdown scheduler first (before container resources)
    if scheduler_service:
        scheduler_service.shutdown()
        _logger.info("Background scheduler stopped.")
    
    # Shutdown all container resources (cache, db sessions, etc.)
    # This properly cleans up all Resource providers
    await app.container.shutdown_resources()
    _logger.info("Container resources shutdown complete.")


app = FastAPI(
    title=f"{settings.OPENAPI_TITLE}",
    description=settings.OPENAPI_DESCRIPTION,
    version=settings.OPENAPI_VERSION,
    docs_url="/docs" if settings.OPENAPI_ENABLED else None,
    redoc_url="/redoc" if settings.OPENAPI_ENABLED else None,
    openapi_url="/openapi.json" if settings.OPENAPI_ENABLED else None,
    lifespan=startup,
)

if settings.OPENAPI_ENABLED:
    app.openapi = lambda: custom_openapi(app)

# Create container with declarative configuration
# All providers are defined at class level - no runtime modifications
container = Container()
app.container = container

# Rate limiting middleware - runs first (outermost)
# Uses cache service (memory or Redis) for distributed rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production [e.g., specific domains]
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.add_middleware(CustomExceptionMiddleware)
app.exception_handler(RequestValidationError)(custom_validation_exception_middleware)

app.include_router(v1_routers, prefix="/api/v1")


@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint to verify the application is running."""
    return {"status": "healthy"}
