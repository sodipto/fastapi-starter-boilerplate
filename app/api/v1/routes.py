from fastapi import APIRouter

from app.api.v1.endpoints.user import router as user_router

routers = APIRouter()
router_list = [user_router]

for router in router_list:
    routers.include_router(router)
