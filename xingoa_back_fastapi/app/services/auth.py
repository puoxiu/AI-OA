from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.models.user import OAUser, OADepartment, DepartmentUserRole

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
    async def get_user_by_email(db_session: AsyncSession, email: str) -> OAUser | None:
        query = (
            select(OAUser)
            .where(OAUser.email == email)
            .options(
                # 预加载用户的部门角色信息（避免后续查询数据库）
                selectinload(OAUser.department_roles)
                .joinedload(DepartmentUserRole.department)  # 同时加载部门详情
            )
        )
        result = await db_session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_user_by_username(db_session: AsyncSession, username: str):
        query = (
            select(OAUser)
            .where(OAUser.username == username)
            .options(
                # 预加载关联数据，按需选择
                selectinload(OAUser.department_roles)
                .joinedload(DepartmentUserRole.department),
                # 如需其他关联数据（如用户的预订记录），可在此添加
                # selectinload(OAUser.booked_meetings)
            )
        )
        result = await db_session.execute(query)
        return result.scalars().first()