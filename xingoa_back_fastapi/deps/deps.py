# deps.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

from db.database import async_session
from app.core.auth import AuthTokenHelper
from app.models.user import OAUser
from app.services.auth import UserService
from app.exceptions import BizException
from app.error import ErrorCode

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_session = None
    try:
        db_session = async_session()
        yield db_session
    finally:
        await db_session.close()

# 别搞错了，令牌如果不是tokenUrl路径获取的 则不能用get_current_user获取用户
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

async def get_current_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = AuthTokenHelper.token_decode(token)
        print(f"成功获取payload: {payload}")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload is None:
        raise BizException(ErrorCode.TOKEN_ERROR, 400)
    return payload


async def get_current_user(
    payload: dict = Depends(get_current_payload),
    db_session: AsyncSession = Depends(get_db_session)
) -> OAUser:
    user = await UserService.get_user_by_email(db_session, email=payload["email"])
    if not user:
        raise BizException(ErrorCode.TOKEN_ERROR, 400)
    return user
