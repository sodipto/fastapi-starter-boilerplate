from contextlib import asynccontextmanager

from fastapi.exceptions import RequestValidationError

from app.core.container import Container
from app.core.config import settings
from fastapi import FastAPI

from app.api.endpoints.routes import routers as v1_routers
from app.core.database.migrate import run_pending_migrations
from app.core.middlewares.exception_middleware import CustomExceptionMiddleware
from app.core.middlewares.validation_exception_middleware import custom_validation_exception_middleware
from app.core.open_api import custom_openapi
from app.core.seeders.application import ApplicationSeeder

@asynccontextmanager
async def startup(app: FastAPI):
    print("Starting up application...")
    if settings.DATABASE_ENABLED:
        run_pending_migrations()
        try:
            await ApplicationSeeder().seed_data()
        except Exception as e:
            print(f"Seeding failed: {e}")
            raise SystemExit("Application startup aborted due to seeding failure.")
    yield

    # Shutdown
    print("Shutting down application...")
    
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
app.add_middleware(CustomExceptionMiddleware)
app.exception_handler(RequestValidationError)(custom_validation_exception_middleware)

app.include_router(v1_routers, prefix="/api/v1")
