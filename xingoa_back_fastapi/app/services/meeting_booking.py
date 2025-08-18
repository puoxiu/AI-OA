# app/services/meeting_booking.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.models.meeting_room import MeetingBooking, MeetingRoom
from app.schemas.meeting_booking import MeetingBookingCreate
from app.exceptions import BizException
from app.error import ErrorCode
from app.models.user import OAUser
from sqlalchemy import or_

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
    async def get_meeting_room(db: AsyncSession, room_id: int) -> MeetingRoom:
        """获取会议室信息并验证是否存在且可用"""
        query = select(MeetingRoom).where(MeetingRoom.id == room_id)
        result = await db.execute(query)
        room = result.scalar_one_or_none()
        
        if not room:
            raise BizException(ErrorCode.NOT_FOUND, "会议室不存在")
            
        if not room.is_active:
            raise BizException(ErrorCode.PARAM_ERROR, "该会议室不可用")
            
        return room
    
    @staticmethod
    async def validate_booking_time(start_time: datetime, end_time: datetime):
        """验证预订时间是否合理"""
        # 检查开始时间是否在结束时间之前
        if start_time >= end_time:
            raise BizException(ErrorCode.PARAM_ERROR, "结束时间必须晚于开始时间")
        
        # 检查是否预订过去的时间
        now = datetime.now()
        if start_time < now - timedelta(minutes=5):  # 允许5分钟的误差
            raise BizException(ErrorCode.PARAM_ERROR, "不能预订过去的时间")
            
        # 检查预订时长是否合理（最长不超过24小时）
        if (end_time - start_time) > timedelta(hours=24):
            raise BizException(ErrorCode.PARAM_ERROR, "单次预订最长不能超过24小时")
            
        # 检查是否提前预订（至少提前10分钟）
        if start_time < now + timedelta(minutes=10):
            raise BizException(ErrorCode.PARAM_ERROR, "请至少提前10分钟预订会议室")
    
    @staticmethod
    async def create_booking(
        db: AsyncSession, 
        booking_data: MeetingBookingCreate, 
        current_user: OAUser
    ) -> MeetingBooking:
        """创建会议室预订"""
        # 1.验证会议室是否存在且可用
        room = await MeetingBookingService.get_meeting_room(db, booking_data.room_id)
        # 2.验证预订时间是否合理
        await MeetingBookingService.validate_booking_time(booking_data.start_time, booking_data.end_time)
        # 3.检查会议室是否可用（无时间冲突）
        is_available = await MeetingBookingService.check_room_availability(
            db, 
            booking_data.room_id, 
            booking_data.start_time, 
            booking_data.end_time
        )
        if not is_available:
            raise BizException(ErrorCode.BOOKING_TIME_CONFLICT)

        # 4.创建预订记录
        booking = MeetingBooking(
            title=booking_data.title,
            description=booking_data.description,
            room_id=booking_data.room_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            booker_id=current_user.id,
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking


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
        current_user: OAUser
    ) -> bool:
        """取消预订（仅预订人或管理员可操作）"""
        result = await db.execute(
            select(MeetingBooking).where(MeetingBooking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            raise BizException(ErrorCode.NOT_FOUND, "预订记录不存在")
            
        # 验证权限（预订人或管理员）
        if booking.booker_id != current_user.id and current_user.is_superuser:
            # 这里可以添加管理员权限检查
            raise BizException(ErrorCode.NOT_PERMITTED, 403, "您没有权限取消该预订")
        
        # 检查是否可以取消（至少提前30分钟取消）
        now = datetime.now()
        if booking.start_time - now < timedelta(minutes=30):
            raise BizException(ErrorCode.BUSINESS_ERROR, 400, "会议开始前30分钟内不可取消")
        
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
        await MeetingBookingService.validate_booking_time(start_time, end_time)
        
        # 1. 先查询所有活跃的会议室
        active_rooms_query = select(MeetingRoom).where(MeetingRoom.is_active == True)
        result = await db.execute(active_rooms_query)
        active_rooms = result.scalars().all()
        
        available_rooms = []
        for room in active_rooms:
            # 2. 检查每个会议室在指定时间段是否可用
            # 使用已有的检查方法，确保逻辑一致性
            is_available = await MeetingBookingService.check_room_availability(
                db, room.id, start_time, end_time
            )
            if is_available:
                available_rooms.append(room)
        
        return available_rooms
    