from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

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

    # 日志配置
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_DIR: str = "logs"
    LOG_FILE: str = "app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    LOG_CONSOLE_OUTPUT: bool = False


    class Config:
        env_file = ".env"



@lru_cache
def get_settings():
    return Settings()


settings = get_settings()