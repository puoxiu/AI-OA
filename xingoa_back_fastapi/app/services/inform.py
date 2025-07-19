from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy import or_


from app.models.user import OAUser, OADepartment
from app.models.inform import Inform, InformRead, InformDepartment
from app.schemas.inform import InformsResponse

class InformService:
    @staticmethod
    # 查看所有可见的通知：public：true 或者 作者是当前用户 或者 通知的可见部门包含当前用户部门
    async def get_informs(db_session: AsyncSession, user: OAUser):
        query = select(Inform).options(selectinload(Inform.author), selectinload(Inform.departments))\
            .where(
                or_(
                    Inform.public == True,
                    Inform.author_id == user.uid,
                    Inform.departments.any(OADepartment.id == user.department_id)
                )
            ).order_by(Inform.create_time.desc())
        result = await db_session.execute(query)
        informs = result.scalars().all()
        # 检查已读状态
        read_result = await db_session.execute(
            select(InformRead.inform_id).where(InformRead.user_id == user.uid)
        )
        read_ids = {row[0] for row in read_result.fetchall()}
        return [
            InformsResponse(
                id=inform.id,
                title=inform.title,
                content=inform.content,
                author_id=inform.author_id,
                author_name=inform.author.username,
                create_time=inform.create_time,
                is_read=inform.id in read_ids
            )
            for inform in informs
        ]



    @staticmethod
    async def get_inform_by_id(db_session: AsyncSession, inform_id: int):
        query = select(Inform).where(Inform.id == inform_id)
        result = await db_session.execute(query)
        return result.scalar()


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


    # 已读

    @staticmethod
    async def mark_inform_as_read(db: AsyncSession, inform_id: int, user: OAUser):
        # 检查是否已读
        result = await db.execute(
            select(InformRead).where(
                InformRead.inform_id == inform_id,
                InformRead.user_id == user.uid
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return {"message": "Already marked as read."}

        # 插入已读记录
        read = InformRead(inform_id=inform_id, user_id=user.uid)
        db.add(read)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return {"message": "Already marked as read (duplicate)."}
        return {"message": "Marked as read successfully."}