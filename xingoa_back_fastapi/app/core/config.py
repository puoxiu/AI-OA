from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "xingoa_基于AI的OA系统"
    APP_VERSION: str = "1.0.0"

    ASYNC_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int

    # 基础URL 用于生成激活链接
    BASE_URL: str
    # 用于加密的密钥
    SECRET_KEY: str

    # 邮件服务
    EMAIL_FROM: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # celery 配置
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    class Config:
        env_file = ".env"



@lru_cache
def get_settings():
    return Settings()


settings = get_settings()