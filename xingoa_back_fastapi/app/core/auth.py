from jose import jwt
from datetime import datetime, timedelta

from core.config import settings

from datetime import datetime, timezone


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
        except jwt.ExpiredSignatureError:
            # Token 已过期
            return None
        except jwt.InvalidTokenError:
            # Token 无效
            return None