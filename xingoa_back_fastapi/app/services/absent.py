# AI-OA/xingoa_back_fastapi/app/services/absent.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.absent import Absent, AbsentType
from app.schemas.absent import AbsentCreateRequest, AbsentUpdate
from typing import Optional

class AbsentService:
    @staticmethod
    async def create_absent(db: AsyncSession, absent: AbsentCreateRequest, requester_id: int, responder_id: Optional[int]):
        db_absent = Absent(
            title=absent.title,
            request_content=absent.request_content,
            absent_type_id=absent.absent_type_id,
            start_date=absent.start_date,
            end_date=absent.end_date,
            requester_id=requester_id,
            responder_id=responder_id
        )
        db.add(db_absent)
        await db.commit()
        await db.refresh(db_absent)
        return db_absent

    @staticmethod
    async def get_absents(db: AsyncSession, requester_id: Optional[int] = None, responder_id: Optional[int] = None):
        query = select(Absent)
        if requester_id:
            query = query.where(Absent.requester_id == requester_id)
        if responder_id:
            query = query.where(Absent.responder_id == responder_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_absent_by_id(db: AsyncSession, absent_id: int):
        result = await db.execute(select(Absent).where(Absent.id == absent_id))
        return result.scalar_one_or_none()
    
    # @staticmethod
    # async def update_absent(db: AsyncSession, absent_id: int, absent_update: AbsentUpdate):
    #     query = (
    #         update(Absent)
    #         .where(Absent.id == absent_id)
    #         .values(**absent_update.dict(exclude_unset=True))
    #     )
    #     await db.execute(query)
    #     await db.commit()
    #     absent = await get_absent_by_id(db, absent_id)
    #     return absent