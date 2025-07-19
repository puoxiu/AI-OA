from fastapi import HTTPException, status, Depends
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from deps.deps import get_db_session
from .auth import AuthTokenHelper
from app.services.auth import UserService
from app.models.user import OAUser

# 获取当前用户

async def get_current_user(token: str = Depends(AuthTokenHelper.get_token), db_session: AsyncSession = Depends(get_db_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("=====")
    try:
        payload = AuthTokenHelper.token_decode(token)
        if payload is None:
            raise credentials_exception
        email = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await UserService.get_user_by_email(db_session, email)
    if user is None:
        raise credentials_exception
    return user