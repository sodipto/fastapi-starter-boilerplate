# from app.core.logging import setup_logging
# setup_logging()
import logging

from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.container import Container
from app.core.config import settings
from fastapi import FastAPI

from app.api.endpoints.routes import routers as v1_routers
from app.core.database.migrate import run_pending_migrations
from app.core.middlewares.exception_middleware import CustomExceptionMiddleware
from app.core.middlewares.validation_exception_middleware import custom_validation_exception_middleware
from app.core.open_api import custom_openapi
from app.core.seeders.application import ApplicationSeeder
from app.jobs import register_all_jobs
from app.services.cache.cache_factory import init_cache_service, shutdown_cache_service

logger = logging.getLogger("app.main")

@asynccontextmanager
async def startup(app: FastAPI):
    logger.info("Starting up application...")
    logger.info("Application startup initiated.")
    if settings.DATABASE_ENABLED:
        run_pending_migrations()
        try:
            await ApplicationSeeder().seed_data()
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            raise SystemExit("Application startup aborted due to seeding failure.")
    
    # Initialize cache service
    cache_service = await init_cache_service()
    app.state.cache_service = cache_service
    # Inject cache_service into the DI container
    app.container.cache_service.override(cache_service)
    logger.info(f"Cache service initialized (type: {settings.CACHE_TYPE})")
    
    # Initialize and start the background scheduler
    scheduler_service = None
    if settings.BACKGROUND_JOBS_ENABLED:
        scheduler_service = app.container.scheduler_service()
        register_all_jobs(scheduler_service)
        scheduler_service.start()
        logger.info("Background scheduler started.")
    
    yield

    # Shutdown
    logger.info("Shutting down application...")
    
    # Shutdown cache service
    if hasattr(app.state, "cache_service"):
        await shutdown_cache_service(app.state.cache_service)
        logger.info("Cache service shutdown.")
    
    # Shutdown scheduler
    if scheduler_service:
        scheduler_service.shutdown()
        logger.info("Background scheduler stopped.")
    
app = FastAPI(
    title=f"Python FastAPI Boilerplate - {settings.ENV.capitalize()}",
    description="A robust FastAPI boilerplate for rapid API development, featuring dependency injection, modular routing, and environment-based configuration.",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    lifespan=startup,
)

app.openapi = lambda: custom_openapi(app)
container = Container() 
container.init_resources()
app.container = container

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
