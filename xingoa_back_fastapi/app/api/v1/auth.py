from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone


from app.schemas.user import LoginRequest, LoginResponse, ResetPwdRequest, ResetPwdResponse
from app.models.user import OAUser, UserStatusChoices
from deps.deps import get_db_session
from app.services.auth import UserService
from utils.hash import verify_password, get_password_hash
from app.core.auth import AuthTokenHelper


router = APIRouter(
    prefix="/api/v1/user",
    tags=["用户管理"]
)

@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest, db_session: AsyncSession = Depends(get_db_session)):
    try:
        user = await UserService.get_user_by_email(db_session, login_request.email)
        if not user:
            raise HTTPException(status_code=400, detail="email或者密码错误!")
        
        if not verify_password(login_request.password, user.password_hashed):
            raise HTTPException(status_code=400, detail="email 或密码错误2")
        
        if user.status == UserStatusChoices.UNACTIVED:
            raise HTTPException(status_code=400, detail="该用户尚未激活！")
        elif user.status == UserStatusChoices.LOCKED:
            raise HTTPException(status_code=400, detail="该用户已被锁定，请联系管理员！")
        
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

        return LoginResponse(
            token = token,
            user = user_dict
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/resetpwd", response_model=ResetPwdResponse)
async def resetpwd(resetpwd_request: ResetPwdRequest, db_session: AsyncSession = Depends(get_db_session)):
    try:
        user = await UserService.get_user_by_email(db_session, resetpwd_request.email)
        if not user:
            raise HTTPException(status_code=400, detail="该邮箱对应的用户不存在！")

        # 验证验证码和新密码

        user.password_hashed = get_password_hash(resetpwd_request.new_pwd1)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # 删除 Redis 中的验证码
        return {"message": "密码重置成功"}
    
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


