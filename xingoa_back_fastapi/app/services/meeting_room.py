# app/services/meeting_room.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, insert
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import selectinload

from app.schemas.meeting_room import MeetingRoomCreate, MeetingRoomUpdate
from app.services.inform import InformService  # 复用通知服务
from app.models.user import OAUser, OADepartment
from app.models.meeting_room import (
    MeetingRoom, 
)

class MeetingRoomService:
    # 会议室管理
    @staticmethod
    async def create_room(db: AsyncSession, room_data: MeetingRoomCreate):
        """创建会议室"""
        db_room = MeetingRoom(**room_data.dict())
        db.add(db_room)
        await db.commit()
        await db.refresh(db_room)
        return db_room
    
    @staticmethod
    async def get_rooms(db: AsyncSession, is_active: Optional[bool] = None) -> List[MeetingRoom]:
        """获取会议室列表（支持筛选是否可用）"""
        query = select(MeetingRoom)
        if is_active is not None:
            query = query.filter(MeetingRoom.is_active == is_active)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_room(db: AsyncSession, room_id: int) -> Optional[MeetingRoom]:
        """获取会议室详情"""
        return await db.get(MeetingRoom, room_id)
    
    @staticmethod
    async def update_room(db: AsyncSession, room_id: int, update_data: MeetingRoomUpdate):
        """更新会议室信息"""
        room = await db.get(MeetingRoom, room_id)
        if not room:
            return None
        for k, v in update_data.dict(exclude_unset=True).items():
            setattr(room, k, v)
        db.add(room)
        await db.commit()
        await db.refresh(room)
        return room
    
    @staticmethod
    async def delete_room(db: AsyncSession, room_id: str) -> bool:
        """删除会议室（软删除，标记为不可用）"""
        room = await db.get(MeetingRoom, room_id)
        if not room:
            return False
        room.is_active = False
        db.add(room)
        await db.commit()
        return True
