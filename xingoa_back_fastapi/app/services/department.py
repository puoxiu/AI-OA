from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from app.models.user import OADepartment
from app.schemas.department import DepartmentResponse


class DepartmentService:
    @staticmethod
    async def get_all_departments(db_session: AsyncSession):
        query = select(OADepartment).options(
            selectinload(OADepartment.leader),
            selectinload(OADepartment.manager)
        )
        result = await db_session.execute(query)
        departments = result.scalars().all()
        return [DepartmentResponse(**department.__dict__) for department in departments]

