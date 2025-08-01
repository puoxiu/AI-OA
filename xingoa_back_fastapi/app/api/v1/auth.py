from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone


from app.schemas.user import LoginRequest, LoginResponse, ResetPwdRequest
from app.models.user import OAUser, UserStatusChoices
from deps.deps import get_db_session
from app.services.auth import UserService
from utils.hash import verify_password, get_password_hash
from app.core.auth import AuthTokenHelper
from app.response_model import BaseResponse
from app.error import ErrorCode
from app.exceptions import BizException
from app.core.logging import app_logger

router = APIRouter(
    prefix="/api/v1/user",
    tags=["用户管理"]
)

@router.post("/login", response_model=BaseResponse[LoginResponse])
async def login(login_request: LoginRequest, db_session: AsyncSession = Depends(get_db_session)):
    user = await UserService.get_user_by_email(db_session, login_request.email)
    if not user:
        raise BizException(ErrorCode.LOGIN_ERROR, 400)
    
    if not verify_password(login_request.password, user.password_hashed):
        raise BizException(ErrorCode.LOGIN_ERROR, 400)
    
    if user.status == UserStatusChoices.UNACTIVED:
        raise BizException(ErrorCode.USER_NOT_ACTIVED, 400)
    elif user.status == UserStatusChoices.LOCKED:
        raise BizException(ErrorCode.USER_LOCKED, 400)
    
    # user.last_login = datetime.utcnow()
    user.last_login = datetime.now(timezone.utc)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    payload = {
        'sub': 'xingxing',
        'email': user.email,
        'username': user.username,
        'scopes': ["user"],  # 可选
    }

    # 暂时不返回用户信息
    user_dict = {
        "uid": user.uid,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "is_staff": user.is_staff,
        "status": user.status,
        "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if user.date_joined else None,
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
    }
    token = AuthTokenHelper.token_encode(payload)
    
    app_logger.info(f"用户登录成功，用户：{user.uid}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="登录成功",
        data=LoginResponse(
            token=token,
            user=user_dict
        )
    )
    

@router.post("/resetpwd", response_model=BaseResponse)
async def resetpwd(resetpwd_request: ResetPwdRequest, db_session: AsyncSession = Depends(get_db_session)):
    user = await UserService.get_user_by_email(db_session, resetpwd_request.email)
    if not user:
        raise BizException(ErrorCode.LOGIN_ERROR, 400)

    # 验证验证码和新密码

    user.password_hashed = get_password_hash(resetpwd_request.new_pwd1)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    app_logger.info(f"用户密码重置成功，用户：{user.uid}")
    
    # 删除 Redis 中的验证码
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="密码重置成功"
    )



