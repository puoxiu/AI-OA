from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List

from app.models.user import OADepartment, OAUser, DepartmentUserRole
from app.models.inform import Inform, InformRead
from app.models.absent import Absent, AbsentType
from app.schemas.home import (
    LatestInformResponse,
    LatestAbsentResponse,
    DepartmentStaffCountResponse
)
from sqlalchemy import or_

class HomeService:
    # 获取最新10条通知
    @staticmethod
    async def get_latest_informs(db_session: AsyncSession, current_user: OAUser) -> List[LatestInformResponse]:
        # 获取用户所属部门ID
        dept_ids = [role.department_id for role in current_user.department_roles]
        
        # 查询可见通知（公共/本部门/自己发布）
        query = select(Inform).options(
            selectinload(Inform.author)
        ).where(
            or_(
                Inform.public == True,
                Inform.author_id == current_user.id,
                Inform.departments.any(OADepartment.id.in_(dept_ids))
            )
        ).order_by(Inform.create_time.desc()).limit(10)
        
        result = await db_session.execute(query)
        informs = result.scalars().all()
        
        # 获取已读记录
        read_ids = {
            row[0] for row in (await db_session.execute(
                select(InformRead.inform_id).where(InformRead.user_id == current_user.id)
            )).fetchall()
        }
        
        return [
            LatestInformResponse(
                id=inform.id,
                title=inform.title,
                author_name=inform.author.username,
                create_time=inform.create_time,
                is_read=inform.id in read_ids
            ) for inform in informs
        ]

    # 获取最新10条考勤记录
    @staticmethod
    async def get_latest_absents(db_session: AsyncSession, current_user: OAUser) -> List[LatestAbsentResponse]:
        # 董事会成员可看所有，否则只能看本部门
        query = select(Absent).options(
            selectinload(Absent.requester),
            selectinload(Absent.absent_type)
        )
        
        # 检查用户是否属于董事会
        is_board_member = any(
            role.department.name == "董事会" 
            for role in current_user.department_roles
        )
        
        if not is_board_member:
            # 过滤本部门
            user_dept_ids = [role.department_id for role in current_user.department_roles]
            query = query.where(
                Absent.requester.has(
                    OAUser.department_roles.any(
                        DepartmentUserRole.department_id.in_(user_dept_ids)
                    )
                )
            )
        
        # 取最新10条
        query = query.order_by(Absent.create_time.desc()).limit(10)
        result = await db_session.execute(query)
        absents = result.scalars().all()
        
        return [
            LatestAbsentResponse(
                id=absent.id,
                requester_name=absent.requester.username,
                absent_type_name=absent.absent_type.name,
                start_date=absent.start_date,
                end_date=absent.end_date,
                status=absent.status,
                create_time=absent.create_time
            ) for absent in absents
        ]

    # 部门员工数量统计
    @staticmethod
    async def get_department_staff_count(db_session: AsyncSession) -> List[DepartmentStaffCountResponse]:
        # 统计每个部门的用户数量
        query = select(
            OADepartment.name,
            func.count(DepartmentUserRole.user_id).label("staff_count")
        ).join(
            DepartmentUserRole, OADepartment.id == DepartmentUserRole.department_id
        ).group_by(OADepartment.name)
        
        result = await db_session.execute(query)
        data = result.fetchall()
        
        return [
            DepartmentStaffCountResponse(
                name=item.name,
                staff_count=item.staff_count
            ) for item in data
        ]