# deps.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from db.database import async_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_session = None
    try:
        db_session = async_session()
        yield db_session
    finally:
        await db_session.close()


