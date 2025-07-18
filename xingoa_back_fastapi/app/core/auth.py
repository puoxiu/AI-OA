from jose import jwt
from datetime import datetime, timedelta

from app.core.config import settings

from datetime import datetime, timezone
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class AuthTokenHelper:
    @staticmethod
    def token_encode(payload: dict) -> str:
        to_data = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)
        to_data.update({"exp": expire})

        return jwt.encode(to_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def token_decode(token)-> dict:
        # payload
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            return payload
        # todo ？ 
        except jwt.ExpiredSignatureError:
            # Token 已过期
            return None
        except:
            # Token 无效
            return None

    @staticmethod
    def get_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
        """从请求头中获取并验证令牌"""
        if not credentials:
            raise HTTPException(status_code=401, detail="认证失败")
        return credentials.credentials