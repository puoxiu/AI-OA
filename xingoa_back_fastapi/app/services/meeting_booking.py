# app/services/meeting_booking.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.meeting_room import MeetingBooking, MeetingRoom
from app.schemas.meeting_booking import MeetingBookingCreate
from app.exceptions import BizException
from app.error import ErrorCode

class MeetingBookingService:
    @staticmethod
    async def check_room_availability(
        db: AsyncSession, 
        room_id: int, 
        start_time: datetime, 
        end_time: datetime,
        exclude_id: Optional[int] = None
    ) -> bool:
        """检查会议室是否可用（无时间冲突）"""
        # 基础查询条件
        conditions = [
            MeetingBooking.room_id == room_id,
            and_(
                MeetingBooking.start_time < end_time,
                MeetingBooking.end_time > start_time
            )
        ]
        
        # 如果是更新操作，排除自身
        if exclude_id:
            conditions.append(MeetingBooking.id != exclude_id)
            
        query = select(MeetingBooking).where(*conditions)
        result = await db.execute(query)
        
        # 存在冲突记录则返回False
        return result.scalar_one_or_none() is None

    @staticmethod
    async def create_booking(
        db: AsyncSession, 
        booking_data: MeetingBookingCreate, 
        booker_id: str
    ) -> MeetingBooking:
        """创建会议室预订"""
        # 检查会议室是否存在
        room = await db.get(MeetingRoom, booking_data.room_id)
        if not room or not room.is_active:
            raise BizException(ErrorCode.NOT_FOUND, 404)
        
        # 检查时间冲突
        is_available = await MeetingBookingService.check_room_availability(
            db, 
            booking_data.room_id,
            booking_data.start_time,
            booking_data.end_time
        )
        if not is_available:
            raise BizException(ErrorCode.BOOKING_TIME_CONFLICT, 400)
        
        # 创建预订记录
        db_booking = MeetingBooking(
            **booking_data.dict(),
            booker_id=booker_id
        )
        db.add(db_booking)
        await db.commit()
        await db.refresh(db_booking)
        return db_booking

    @staticmethod
    async def get_booking(db: AsyncSession, booking_id: int) -> Optional[MeetingBooking]:
        """获取预订详情"""
        return await db.get(
            MeetingBooking, 
            booking_id,
            options=[
                selectinload(MeetingBooking.booker),
                selectinload(MeetingBooking.room)
            ]
        )

    @staticmethod
    async def get_user_bookings(
        db: AsyncSession, 
        booker_id: str
    ) -> List[MeetingBooking]:
        """获取用户的预订记录"""
        query = select(MeetingBooking).where(
            MeetingBooking.booker_id == booker_id
        ).options(
            selectinload(MeetingBooking.room)
        )
            
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_room_bookings(
        db: AsyncSession, 
        room_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MeetingBooking]:
        """获取会议室的预订记录（可按时间筛选）"""
        query = select(MeetingBooking).where(
            MeetingBooking.room_id == room_id
        ).options(
            selectinload(MeetingBooking.booker)
        )
        
        # 时间范围筛选
        if start_time:
            query = query.where(MeetingBooking.end_time >= start_time)
        if end_time:
            query = query.where(MeetingBooking.start_time <= end_time)
            
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def cancel_booking(
        db: AsyncSession, 
        booking_id: int, 
        booker_id: str
    ) -> bool:
        """取消预订（仅预订人或管理员可操作）"""
        booking = await db.get(MeetingBooking, booking_id)
        if not booking:
            return False
            
        # 验证权限（预订人或管理员）
        if booking.booker_id != booker_id:
            # 这里可以添加管理员权限检查
            raise BizException(ErrorCode.NOT_PERMITTED, 403)
        
        # 软删除（实际项目中可根据需求改为状态标记）
        await db.delete(booking)
        await db.commit()
        return True

    @staticmethod
    async def approve_booking(
        db: AsyncSession, 
        booking_id: int, 
        approve: bool,
        operator_id: str  # 审批人ID
    ) -> Optional[MeetingBooking]:
        """审批预订（管理员功能）"""
        booking = await db.get(MeetingBooking, booking_id)
        if not booking:
            return None
            
        # 这里可以添加审批人权限检查
        booking.is_approved = approve
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def get_available_rooms(
        db: AsyncSession,
        start_time: datetime,
        end_time: datetime
    ) -> List[MeetingRoom]:
        """查询指定时间段内所有空闲的会议室"""
        query = select(MeetingRoom).where(
            MeetingRoom.is_active == True,
            ~MeetingRoom.bookings.any(
                and_(
                    MeetingBooking.start_time < end_time,
                    MeetingBooking.end_time > start_time
                )
            )
        ).options(
            selectinload(MeetingRoom.bookings)
        )
        result = await db.execute(query)
        return result.scalars().all()
    