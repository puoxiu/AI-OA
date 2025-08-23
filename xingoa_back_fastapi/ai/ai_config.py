from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AI_Settings(BaseSettings):
    # 应用配置
    AI_API_KEY: str
    AI_BASE_URL: str
    AI_MODEL_NAME: str


    MESSAGE_EXPIRE_TIME: int
    MESSAGE_MAX_LENGTH: int
    SESSION_EXPIRE_TIME: int

    # ai 日志配置
    AI_LOG_LEVEL: LogLevel = LogLevel.INFO
    AI_LOG_DIR: str = "logs"
    AI_LOG_FILE: str = "ai.log"
    AI_LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    AI_LOG_BACKUP_COUNT: int = 5
    AI_LOG_CONSOLE_OUTPUT: bool = False


    class Config:
        env_file = ".ai.env"



@lru_cache
def get_ai_settings():
    return AI_Settings()


ai_settings = get_ai_settings()