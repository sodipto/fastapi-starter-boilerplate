from app.core.container import Container
from app.core.config import settings
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.v1.routes import routers as v1_routers

app = FastAPI(
    title=f"Python FastAPI Boilerplate - {settings.ENV.capitalize()}",
    description="This is a boilerplate for building APIs using FastAPI with dependency injection and other best practices.",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Input your Bearer token to access all endpoints"
        }
    }
    openapi_schema["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.container = Container()

app.include_router(v1_routers, prefix="/api/v1")
