from fastapi import APIRouter
from fastapi.params import Depends
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", summary="Get current user", response_model=dict)
def get_me():
    return {"username": "sodipto", "email": "sodipto.saha@asthait.com"}


@router.get("/{user_id}", summary="Get user by ID", response_model=dict)
@inject
async def get_user_by_id(user_id: int, user_service: UserService = Depends(Provide[Container.user_service])):
    username = await user_service.get_user_name(user_id)
    return {"username": username, "user_id": user_id}
