from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import OADepartment, DepartmentUserRole, DepartmentRoleChoices
from app.schemas.department import DepartmentResponse


class DepartmentService:
    @staticmethod
    async def get_all_departments(db_session: AsyncSession):
        """
        获取所有部门信息:部门名称、部门负责人、部门经理
        :param db_session: 数据库会话
        :return: 部门信息列表
        """
        query = (
            select(OADepartment)
            .join(DepartmentUserRole)
            .filter(
                DepartmentUserRole.role.in_(
                    [DepartmentRoleChoices.LEADER, DepartmentRoleChoices.MANAGER]
                )
            )
            .options(
                selectinload(OADepartment.user_roles)
                .joinedload(DepartmentUserRole.user)
            )
            .distinct()
        )
        result = await db_session.execute(query)
        departments = result.scalars().all()
        department_responses = []

        for dept in departments:
            leader = None
            manager = None

            for user_role in dept.user_roles:
                user = user_role.user
                if user_role.role == DepartmentRoleChoices.LEADER:
                    leader = {"id": user.id, "username": user.username}
                elif user_role.role == DepartmentRoleChoices.MANAGER:
                    manager = {"id": user.id, "username": user.username}
            
            department_responses.append(
                DepartmentResponse(
                    id=dept.id,
                    name=dept.name,
                    leader=leader,
                    manager=manager,
                )
            )
        return department_responses


