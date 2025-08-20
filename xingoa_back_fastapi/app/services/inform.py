from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy import or_


from app.models.user import OAUser, OADepartment, DepartmentUserRole
from app.models.inform import Inform, InformRead, InformDepartment
from app.schemas.inform import InformsResponse
from app.exceptions import BizException
from app.error import ErrorCode

class InformService:
    @staticmethod
    async def get_informs(db_session: AsyncSession, current_user: OAUser) -> list[InformsResponse]:
        """查看所有可见的通知(不返回通知内容)"""

        # 1. 获取当前用户所属的所有部门ID（用户可能属于多个部门）
        department_ids = [role.department_id for role in current_user.department_roles if role.department_id]

        # 2. 查询条件：可见通知 = 公共通知 OR 自己发布的 OR 通知部门包含用户所属部门
        query = (
            select(Inform)
            .options(
                selectinload(Inform.author)
                .selectinload(OAUser.department_roles)  # 加载作者的部门角色关联
                .selectinload(DepartmentUserRole.department),  # 进一步加载部门详情
                selectinload(Inform.departments)
            )
            .where(
                or_(
                    Inform.public == True,
                    Inform.author_id == current_user.id,
                    Inform.departments.any(OADepartment.id.in_(department_ids))
                )
            )
            .order_by(Inform.create_time.desc())
        )

        result = await db_session.execute(query)
        informs = result.scalars().all()

        # 3.检查已读状态
        read_result = await db_session.execute(
            select(InformRead.inform_id)
            .where(InformRead.user_id == current_user.id)
        )
        read_ids = {row[0] for row in read_result.fetchall()}
        return [
            InformsResponse(
                id=inform.id,
                title=inform.title,
                author_id=inform.author_id,
                author_name=inform.author.username,
                is_public=inform.public,
                author_department_name=(
                    inform.author.department_roles[0].department.name 
                    if inform.author.department_roles else "无部门"
                ),
                create_time=inform.create_time,
                is_read=inform.id in read_ids
            )
            for inform in informs
        ]

    @staticmethod
    async def get_inform_by_id(db_session: AsyncSession, current_user: OAUser, inform_id: int) -> Inform | None:
        """根据ID获取通知详情 带权限验证"""
        department_ids = [role.department_id for role in current_user.department_roles if role.department_id]
        query = (
            select(Inform)
            .options(
                selectinload(Inform.author),
                selectinload(Inform.departments)
            )
            .where(
                # 条件1：通知ID匹配; 条件2：用户有权限查看（公共/自己发布/部门可见）
                Inform.id == inform_id,
                or_(
                    Inform.public == True,
                    Inform.author_id == current_user.id,
                    Inform.departments.any(OADepartment.id.in_(department_ids))
                )
            )
        )
        inform = await db_session.scalar(query)

        return inform

    @staticmethod
    async def get_inform_read_record_by_id(db_session: AsyncSession, current_user: OAUser, inform_id: int) -> InformRead | None:
        """根据ID获取通知阅读记录"""
        query = (
            select(InformRead)
            .where(
                InformRead.inform_id == inform_id,
                InformRead.user_id == current_user.id
            )
        )
        read_record = await db_session.scalar(query)

        return read_record

    @staticmethod
    async def create_inform_read_record(db_session: AsyncSession, current_user: OAUser, inform_id: int):
        """创建通知阅读记录"""
        read_record = InformRead(inform_id=inform_id, user_id=current_user.id)
        db_session.add(read_record)
        await db_session.commit()
        await db_session.refresh(read_record)
        return read_record

    @staticmethod
    async def create_inform(db_session: AsyncSession, title: str, content: str,  department_ids: list[int], current_user: OAUser):
        # 1. 处理公开逻辑（0表示全部可见）
        public = 0 in department_ids
        
        # 2. 过滤无效部门ID（移除0和空值）
        valid_department_ids = [
            dept_id for dept_id in department_ids 
            if dept_id is not None and dept_id != 0
        ]
        
        # 3. 校验：非公开通知必须包含有效部门ID
        if not public and not valid_department_ids:
            raise BizException(ErrorCode.INVALID_PARAM, 400, "非公开通知必须指定至少一个部门")
        
        # 4. 创建通知主记录（暂不提交事务）
        inform = Inform(
            title=title,
            content=content,
            public=public,
            author_id=current_user.id,  # 显式关联作者ID
            author=current_user  # 关联作者对象（ORM自动同步）
        )
        db_session.add(inform)
        
        # 5. 处理部门关联（非公开且有有效部门ID时）
        if not public and valid_department_ids:
            # 查询指定的部门是否存在
            result = await db_session.execute(
                select(OADepartment).where(OADepartment.id.in_(valid_department_ids))
            )
            departments = result.scalars().all()
            
            # 校验部门ID有效性
            if len(departments) != len(valid_department_ids):
                existing_ids = {dept.id for dept in departments}
                invalid_ids = [dept_id for dept_id in valid_department_ids if dept_id not in existing_ids]
                raise BizException(ErrorCode.PARAM_ERROR, 400, f"无效的部门ID：{invalid_ids}")
            
            # 创建通知-部门关联记录
            for department in departments:
                inform_department = InformDepartment(
                    inform_id=inform.id,
                    department_id=department.id,
                )
                db_session.add(inform_department)
        
        # 6. 一次性提交所有事务（通知主记录+关联记录）
        await db_session.commit()
        await db_session.refresh(inform)
        
        return inform


    @staticmethod
    async def delete_inform(db_session: AsyncSession, current_user: OAUser, inform_id: int):
        # 1. 校验通知是否存在
        query = select(Inform).where(Inform.id == inform_id)
        inform = await db_session.scalar(query)
        if not inform:
            raise BizException(ErrorCode.NOT_FOUND, 404, "通知不存在")

        # 2. 校验用户是否有权限删除
        if inform.author_id != current_user.id:
            raise BizException(ErrorCode.NOT_PERMITTED, 403, "没有权限删除该通知")

        # 3. 删除通知-部门关联记录
        query = delete(InformDepartment).where(InformDepartment.inform_id == inform_id)
        await db_session.execute(query)

        # 4. 删除通知阅读记录
        query = delete(InformRead).where(InformRead.inform_id == inform_id)
        await db_session.execute(query)

        # 5. 删除通知主记录
        query = delete(Inform).where(Inform.id == inform_id)
        await db_session.execute(query)

        # 6. 提交事务
        await db_session.commit()
        
