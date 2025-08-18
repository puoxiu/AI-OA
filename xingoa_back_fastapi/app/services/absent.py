# AI-OA/xingoa_back_fastapi/app/services/absent.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload
from app.models.absent import Absent, AbsentType
from app.models.user import OAUser, DepartmentUserRole, OADepartment, DepartmentRoleChoices
from app.schemas.absent import AbsentCreateRequest
from typing import Optional
from app.exceptions import BizException
from app.error import ErrorCode


class AbsentTypeService:
    @staticmethod
    async def get_all_absent_type(db_session: AsyncSession):
        query = select(AbsentType).order_by(AbsentType.id)
        result = await db_session.execute(query)
        # return res.all()
        return result.scalars().all()

    @staticmethod
    async def get_absent_type_by_id(db_session: AsyncSession, absent_type_id: int):
        query = select(AbsentType).where(AbsentType.id == absent_type_id)
        result = await db_session.execute(query)
        return result.scalars().first()


class AbsentService:
    @staticmethod
    async def create_absent(db_session: AsyncSession, absent: AbsentCreateRequest, current_user: OAUser, responder: OAUser):
        # 1.判断请假类型是否存在
        absent_type = await AbsentTypeService.get_absent_type_by_id(db_session=db_session, absent_type_id=absent.absent_type_id)
        if not absent_type:
            raise BizException(ErrorCode.NOT_FOUND, 404, "请假类型不存在")
        
        db_absent = Absent(
            title=absent.title,
            request_content=absent.request_content,
            status= 2 if current_user == responder else 1,  # 如果审批者就是自己 则直接通过，1-待审批，2-通过

            start_date=absent.start_date,
            end_date=absent.end_date,

            requester_id=current_user.id,
            requester=current_user,

            responder_id=responder.id,
            responder=responder,

            absent_type_id=absent.absent_type_id,
            absent_type=absent_type,
        )
        db_session.add(db_absent)
        await db_session.commit()
        await db_session.refresh(db_absent)
        return db_absent

    @staticmethod
    async def get_all_absent_by_requester_id(db_session: AsyncSession, requester_id: str, page: int, page_size: int):
        # query = select(Absent).where(Absent.requester_id == requester_id).order_by(Absent.create_time)
        # result = await db_session.execute(query)

        # return result.scalars().all()
        page = max(page, 1)
        offset = (page - 1) * page_size

        # 1.查询当前页数据
        query = (
            select(Absent)
            .where(Absent.requester_id == requester_id)
            .order_by(Absent.create_time)
            .offset(offset)
            .limit(page_size)
        )
        result = await db_session.execute(query)
        cur_page_absents = result.scalars().all()

        # 2.查询总记录数
        query = select(func.count()).select_from(Absent).where(Absent.requester_id == requester_id)
        total_result = await db_session.execute(query)
        total_count = total_result.scalar_one()

        return cur_page_absents, total_count


    @staticmethod
    async def get_all_absent_by_responder_id(db_session: AsyncSession, responder_id: str, page: int, page_size: int):
        # query = select(Absent).where(Absent.responder_id == responder_id).order_by(Absent.create_time)
        # result = await db_session.execute(query)

        # return result.scalars().all()
        page = max(page, 1)
        offset = (page - 1) * page_size

        # 1.查询当前页数据--按照时间倒序
        query = (
            select(Absent)
            .where(Absent.responder_id == responder_id)
            .order_by(Absent.create_time.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await db_session.execute(query)
        cur_page_absents = result.scalars().all()

        # 2.查询总记录数
        query = select(func.count()).select_from(Absent).where(Absent.responder_id == responder_id)
        total_result = await db_session.execute(query)
        total_count = total_result.scalar_one()

        return cur_page_absents, total_count


    
    @staticmethod
    async def get_all_absent_by_responder_id_and_status(db_session: AsyncSession, responder_id: str, status: int, page: int, page_size: int):
        page = max(page, 1)
        offset = (page - 1) * page_size

        # 1.查询当前页数据--按照时间倒序
        query = (
            select(Absent)
            .where(Absent.responder_id == responder_id, Absent.status == status)
            .order_by(Absent.create_time.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await db_session.execute(query)
        cur_page_absents = result.scalars().all()

        # 2.查询总记录数
        query = select(func.count()).select_from(Absent).where(Absent.responder_id == responder_id, Absent.status == status)
        total_result = await db_session.execute(query)
        total_count = total_result.scalar_one()

        return cur_page_absents, total_count
    
    @staticmethod
    async def get_absent_by_id(db_session: AsyncSession, absent_id: int):
        query = select(Absent).where(Absent.id == absent_id)
        result = await db_session.execute(query)
        return result.scalar()

    @staticmethod
    async def update_absent_status(db_session: AsyncSession, absent_id: int, status: int, response_content: str):
        query = (
            update(Absent)
            .where(Absent.id == absent_id)
            .values(status=status, response_content=response_content)
        )
        await db_session.execute(query)
        await db_session.commit()

    
    @staticmethod
    async def get_absent_responder(db_session: AsyncSession, current_user: OAUser):
        """
        获取请假审批人
        """
        stmt = (
            select(DepartmentUserRole, OADepartment.name)
            .join(OADepartment, DepartmentUserRole.department_id == OADepartment.id)
            .where(DepartmentUserRole.user_id == current_user.id)
        )
        result = await db_session.execute(stmt)
        user_roles = result.all()  # 格式：[(user_role对象, 部门名称), ...]

        # 2. 判断用户是否属于董事会（只要有一个部门是董事会即生效）
        is_board_member = any(dept_name == "董事会" for (_, dept_name) in user_roles)
        if is_board_member:
            # 如果是董事会成员 则审批者是自己就行
            return current_user
        

        # 3. 非董事会用户（仅属于一个部门，按角色查找）
        # 取第一个部门角色（非董事会用户仅一个部门）
        main_role, dept_name = user_roles[0]
        user_role_type = main_role.role
        dept_id = main_role.department_id

        # 4. 确定目标审批者角色
        if user_role_type == DepartmentRoleChoices.MEMBER:
            # 成员 → 找部门leader
            target_role = DepartmentRoleChoices.LEADER
        else:
            # leader → 找部门manager
            target_role = DepartmentRoleChoices.MANAGER

        # 5. 查询目标角色的审批者
        approver_stmt = (
            select(OAUser)
            .join(DepartmentUserRole)
            .where(
                DepartmentUserRole.department_id == dept_id,
                DepartmentUserRole.role == target_role
            )
        )
        approver = (await db_session.execute(approver_stmt)).scalars().first()

        if not approver:
            # raise BusinessError(f"部门[{dept_name}]中未找到{target_role}角色的审批者")
            raise BizException(ErrorCode.NOT_FOUND, 404, f"部门[{dept_name}]中未找到{target_role}角色的审批者")

        return approver