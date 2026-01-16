from fastapi import APIRouter

from app.api.endpoints.v1.user import router as user_router
from app.api.endpoints.v1.auth import router as auth_router
from app.api.endpoints.v1.role import router as role_router
from app.api.endpoints.v1.email import router as email_router

routers = APIRouter()
router_list = [user_router, auth_router, role_router, email_router]
for router in router_list:
    routers.include_router(router)
