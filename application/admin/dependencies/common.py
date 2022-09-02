from fastapi import Depends, HTTPException, status
from typing import Any

from ...user.routers.operations.user_crud import get_current_active_user

def get_active_user(current_user : Any = Depends(get_current_active_user)):
    if current_user.is_admin == 1 :
        return current_user
    else :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admin can access this api",
            headers={"WWW-Authenticate": "Bearer"},
        )
