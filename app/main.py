from fastapi import FastAPI

from app.api.v1.routes import routers as v1_routers

app = FastAPI(
    title="Python FastAPI Boilerplate",
    docs_url="/swagger",
    redoc_url="/redoc",
)

app.include_router(v1_routers, prefix="/api/v1")
