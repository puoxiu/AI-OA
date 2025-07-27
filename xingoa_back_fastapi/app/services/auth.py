from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload


from app.models.user import OAUser, OADepartment

# class UserService:
#     @staticmethod
#     async def get_user_by_email(db_session: AsyncSession, email: str) -> OAUser | None:
#         query = (
#             select(OAUser)
#             .where(OAUser.email == email)
#             .options(
#                 selectinload(OAUser.leader_department)
#             )
#         )
#         result = await db_session.execute(query)
#         return result.scalar_one_or_none()
#         # return result.scalars().first()


class UserService:
    @staticmethod
    async def get_user_by_email(db_session: AsyncSession, email: str):
        query = (
            select(OAUser)
            .where(OAUser.email == email)
            .options(
                # 预加载 user.department → department.leader（之前已加）
                selectinload(OAUser.department).selectinload(OADepartment.leader),
                # 新增：预加载 user.leader_department → department.manager
                selectinload(OAUser.leader_department).selectinload(OADepartment.manager)
            )
        )
        result = await db_session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_user_by_username(db_session: AsyncSession, username: str):
        query = (
            select(OAUser)
            .where(OAUser.username == username)
        )
        result = await db_session.execute(query)
        return result.scalars().first()