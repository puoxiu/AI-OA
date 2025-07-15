from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.user import OAUser

class UserService:
    @staticmethod
    async def get_user_by_email(async_session: AsyncSession, email: str) -> OAUser | None:
        result = await async_session.execute(select(OAUser).where(OAUser.email == email))
        return result.scalar_one_or_none()
        # return result.scalars().first()