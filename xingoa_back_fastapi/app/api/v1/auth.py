from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.schemas.user import LoginRequest, LoginResponse
from app.models.user import OAUser, UserStatusChoices
from deps.deps import get_db_session
from app.services.auth import UserService

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest, db_session: AsyncSession = Depends(get_db_session)):
    try:
        user = await UserService.get_user_by_email(db_session, login_request.email)
        if not user:
            raise HTTPException(status_code=400, detail="email或者密码错误!")
        
        if user.status == UserStatusChoices.UNACTIVED:
            raise HTTPException(status_code=400, detail="该用户尚未激活！")
        elif user.status == UserStatusChoices.LOCKED:
            raise HTTPException(status_code=400, detail="该用户已被锁定，请联系管理员！")
        
        user.last_login = datetime.utcnow()
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        payload = {
            'sub': 'xingxing',
            'email': user.email,
            'username': user.username,
            'scopes': ["user"],  # 可选
        }

        user_dict = {
            "uid": user.uid,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "is_staff": user.is_staff,
            "status": user.status,
            "is_active": user.is_active,
            "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if user.date_joined else None,
            "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
        }
        # token = AuthTokenHelper.token_encode(payload)

        return {"token": "token", "user": user_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))