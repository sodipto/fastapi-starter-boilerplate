from fastapi import APIRouter
from fastapi.params import Depends, Security
from dependency_injector.wiring import inject, Provide
from fastapi.security import HTTPAuthorizationCredentials

from app.core.container import Container
from app.core.jwt_security import JWTBearer
from app.services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(JWTBearer())]
)


@router.get("/me", summary="Get current user", response_model=dict)
def get_me():
    return {"username": "sodipto", "email": "sodipto.saha@asthait.com"}


@router.get("/{id}", summary="Get user by ID", response_model=dict)
@inject
async def get_user_by_id(id: int, user_service: UserService = Depends(Provide[Container.user_service])):
    username = await user_service.get_user_name(id)
    return {"username": username, "user_id": id}
