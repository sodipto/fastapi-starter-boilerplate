from app.core.container import Container
from app.core.config import settings
from fastapi import FastAPI

from app.api.v1.routes import routers as v1_routers
from app.core.open_api import custom_openapi

app = FastAPI(
    title=f"Python FastAPI Boilerplate - {settings.ENV.capitalize()}",
    description="A robust FastAPI boilerplate for rapid API development, featuring dependency injection, modular routing, and environment-based configuration.",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
)

app.openapi = lambda: custom_openapi(app)
app.container = Container()

app.include_router(v1_routers, prefix="/api/v1")
