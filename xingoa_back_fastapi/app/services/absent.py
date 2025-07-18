# AI-OA/xingoa_back_fastapi/app/services/absent.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.absent import Absent, AbsentType
from app.schemas.absent import AbsentCreateRequest, AbsentUpdate
from typing import Optional

class AbsentTypeService:
    @staticmethod
    async def get_all_absent_type(db_session: AsyncSession):
        query = select(AbsentType).order_by(AbsentType.id)
        result = await db_session.execute(query)
        # return res.all()
        return result.scalars().all()

class AbsentService:
    @staticmethod
    async def create_absent(db_session: AsyncSession, absent: AbsentCreateRequest, requester_uid: str, responder_uid: Optional[str]):
        db_absent = Absent(
            title=absent.title,
            request_content=absent.request_content,
            absent_type_id=absent.absent_type_id,
            start_date=absent.start_date,
            end_date=absent.end_date,
            requester_uid=requester_uid,
            responder_uid=responder_uid,
            status= 0 if requester_uid != responder_uid else 1  # 如果是大老板 则直接通过
        )
        db_session.add(db_absent)
        await db_session.commit()
        await db_session.refresh(db_absent)
        return db_absent

    @staticmethod
    async def get_all_absent_by_requester_uid(db_session: AsyncSession, requester_uid: str):
        query = select(Absent).where(Absent.requester_uid == requester_uid).order_by(Absent.create_time)
        result = await db_session.execute(query)

        return result.scalars().all()

    @staticmethod
    async def get_all_absent_by_responder_uid(db_session: AsyncSession, responder_uid: str):
        query = select(Absent).where(Absent.responder_uid == responder_uid).order_by(Absent.create_time)
        result = await db_session.execute(query)

        return result.scalars().all()
    
    @staticmethod
    async def get_all_absent_by_responder_uid_and_status(db_session: AsyncSession, responder_uid: str):
        query = (
            select(Absent)
            .where(Absent.responder_uid == responder_uid, Absent.status == 0)
            .order_by(Absent.create_time)
        )
        result = await db_session.execute(query)

        return result.scalars().all()