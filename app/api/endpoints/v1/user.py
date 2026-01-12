import uuid
from fastapi import APIRouter
from fastapi.params import Depends
from dependency_injector.wiring import inject, Provide

from app.core.container import Container
from app.core.identity import get_current_user
from app.core.jwt_security import JWTBearer
from app.schema.response.user import UserResponse
from app.services.interfaces.user_service_interface import IUserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(JWTBearer())]
)


@router.get("/me", summary="Get current user", response_model=dict)
def get_me(user_id: int = Depends(get_current_user)):
    return {"username": "sodipto", "email": "sodipto.saha@asthait.com","id": user_id}


@router.get("/{user_id}", summary="Get user by Id", response_model=UserResponse)
@inject
async def get_by_id(user_id: uuid.UUID, user_service: IUserService = Depends(Provide[Container.user_service])):
    return await user_service.get_by_id(user_id)
