from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy import or_


from app.models.user import OAUser, OADepartment
from app.models.inform import Inform, InformRead, InformDepartment
from app.schemas.inform import InformsResponse

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
                selectinload(Inform.author),
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
    async def create_inform(db_session: AsyncSession, title: str, content: str, public: bool, author: OAUser, departments: list[OADepartment] = None):
        inform = Inform(title=title, content=content, public=public, author=author)
        db_session.add(inform)
        await db_session.commit()
        await db_session.refresh(inform)
        if departments:
            for department in departments:
                inform_department = InformDepartment(inform=inform, department=department)
                db_session.add(inform_department)
        await db_session.commit()
        return inform


    @staticmethod
    async def delete_inform(db_session: AsyncSession, inform_id: int):
        query = delete(Inform).where(Inform.id == inform_id)
        await db_session.execute(query)
        await db_session.commit()
