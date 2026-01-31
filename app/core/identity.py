from uuid import UUID
from fastapi import HTTPException
from fastapi.params import Depends
from pydantic import ValidationError
from app.core.jwt_security import JWTBearer
from app.core.config import settings
from app.utils.auth_utils import ALGORITHM
from jose import JWTError, jwt




def get_current_user(token: str = Depends(JWTBearer())
) -> UUID:
    """
    Extract and validate the current user ID from JWT token.
    
    This dependency is used throughout the application to get
    the authenticated user's ID from the JWT bearer token.
    
    Args:
        token: JWT token extracted by JWTBearer dependency
        
    Returns:
        UUID: The user's unique identifier
        
    Raises:
        HTTPException 401: If token is invalid or user_id is missing
        HTTPException 404: If user_id is not found in token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            user_id = UUID(user_id)
            
    except (JWTError, ValidationError, ValueError):
        raise HTTPException(status_code=401, detail="Could not validate credentials!")
    
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found!")
    
    return user_id