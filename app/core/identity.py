from fastapi import HTTPException
from fastapi.params import Depends
from pydantic import ValidationError
from app.core.jwt_security import JWTBearer
from app.core.config import settings
from app.utils.auth_utils import ALGORITHM
from jose import JWTError, jwt




def get_current_user(token: str = Depends(JWTBearer())
) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        user_id= payload["user_id"]
    except (JWTError, ValidationError):
        raise HTTPException(status_code=401,detail="Could not validate credentials!")
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found!")
    return user_id