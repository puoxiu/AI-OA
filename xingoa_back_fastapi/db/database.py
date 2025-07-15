from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


# 定义异步引擎
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # 确保连接有效性
    pool_size=5,
    max_overflow=10
)

# 创建ORM模型的基类
Base = declarative_base()
# 创建异步会话工厂
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)