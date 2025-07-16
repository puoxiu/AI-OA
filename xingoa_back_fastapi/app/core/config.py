from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "xingoa_基于AI的OA系统"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"



@lru_cache
def get_settings():
    return Settings()


settings = get_settings()