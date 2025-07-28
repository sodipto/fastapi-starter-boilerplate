from contextlib import asynccontextmanager
from app.core.container import Container
from app.core.config import settings
from fastapi import FastAPI

from app.api.v1.routes import routers as v1_routers
from app.core.database.migrate import run_pending_migrations
from app.core.open_api import custom_openapi

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_pending_migrations()
    yield
    
app = FastAPI(
    title=f"Python FastAPI Boilerplate - {settings.ENV.capitalize()}",
    description="A robust FastAPI boilerplate for rapid API development, featuring dependency injection, modular routing, and environment-based configuration.",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.openapi = lambda: custom_openapi(app)
container = Container() 
container.init_resources()
app.container = container

app.include_router(v1_routers, prefix="/api/v1")
