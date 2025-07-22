from fastapi import APIRouter

from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.auth import router as auth_router

routers = APIRouter()
router_list = [user_router, auth_router]

for router in router_list:
    routers.include_router(router)
