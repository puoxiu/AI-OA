# app/api/v1/meeting_booking.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.schemas.meeting_booking import (
    MeetingBookingCreate, MeetingBookingResponse
)
from app.services.meeting_booking import MeetingBookingService
from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser
from app.error import ErrorCode
from app.exceptions import BizException
from app.response_model import BaseResponse
from app.core.logging import app_logger

router = APIRouter(
    prefix="/api/v1/meeting-booking",
    tags=["会议室预订"]
)

@router.post("", response_model=BaseResponse[MeetingBookingResponse])
async def create_booking(
    booking: MeetingBookingCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """创建会议室预订"""
    try:
        booking = await MeetingBookingService.create_booking(
            db, booking, current_user.uid
        )
        app_logger.info(f"用户 {current_user.uid} 创建会议室预订：{booking.id}")
        return BaseResponse(
            code=ErrorCode.SUCCESS,
            msg="预订成功",
            data=booking
        )
    except BizException as e:
        raise e
    except Exception as e:
        app_logger.error(f"创建预订失败：{str(e)}")
        raise BizException(ErrorCode.SERVER_ERROR, 500)

@router.get("/{booking_id}", response_model=BaseResponse[MeetingBookingResponse])
async def get_booking_detail(
    booking_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """获取预订详情"""
    booking = await MeetingBookingService.get_booking(db, booking_id)
    if not booking:
        raise BizException(ErrorCode.NOT_FOUND, 404)
    
    # 权限检查：只能查看自己的预订或管理员查看所有
    if booking.booker_id != current_user.uid and current_user.department.name not in ["人事部", "董事会"]:
        raise BizException(ErrorCode.NOT_PERMITTED, 403)
    
    app_logger.info(f"用户 {current_user.uid} 查看预订详情：{booking_id}")
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取成功",
        data=booking
    )

@router.get("/my/{id}", response_model=BaseResponse[List[MeetingBookingResponse]])
async def get_my_bookings(
    id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """获取当前用户的预订记录"""
    bookings = await MeetingBookingService.get_user_bookings(
        db, current_user.uid
    )
    app_logger.info(f"用户 {current_user.uid} 获取个人预订列表")
    print(bookings)
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg=f"获取成功{id}",
        data=bookings
    )



@router.get("/room/{room_id}", response_model=BaseResponse[List[MeetingBookingResponse]])
async def get_room_bookings(
    room_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """获取指定会议室的预订记录"""
    bookings = await MeetingBookingService.get_room_bookings(
        db, room_id, start_time, end_time
    )
    app_logger.info(f"用户 {current_user.uid} 获取会议室 {room_id} 的预订列表")
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取成功",
        data=bookings
    )

@router.delete("/{booking_id}", response_model=BaseResponse)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """取消预订（仅预订人或管理员）"""
    try:
        success = await MeetingBookingService.cancel_booking(
            db, booking_id, current_user.uid
        )
        if not success:
            raise BizException(ErrorCode.NOT_FOUND, 404)
        
        app_logger.info(f"用户 {current_user.uid} 取消预订：{booking_id}")
        return BaseResponse(
            code=ErrorCode.SUCCESS,
            msg="取消成功"
        )
    except BizException as e:
        raise e
    except Exception as e:
        app_logger.error(f"取消预订失败：{str(e)}")
        raise BizException(ErrorCode.SERVER_ERROR, 500)

# 不需要审批 自动通过
