# app/api/v1/meeting_room.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.schemas.meeting_room import (
    MeetingRoomCreate, MeetingRoomResponse, MeetingRoomUpdate,
)
from app.services.meeting_room import MeetingRoomService
from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser
from app.error import ErrorCode
from app.exceptions import BizException
from app.response_model import BaseResponse
from app.core.logging import app_logger

router = APIRouter(
    prefix="/api/v1/meeting-room",
    tags=["会议室管理"]
)

# 会议室CRUD
@router.post("", response_model=BaseResponse[MeetingRoomResponse])
async def create_room(
    room: MeetingRoomCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """创建会议室（仅管理员/人事部）"""
    current_user_id = current_user.id  # 此时会话正常，id已加载，不会触发额外查询

    if not current_user.is_superuser:
        user_departments = {
            role.department.name 
            for role in current_user.department_roles if role.department
        }
        if "人事部" not in user_departments:
            app_logger.error(f"用户 {current_user_id} 没有权限创建会议室")
            raise BizException(ErrorCode.NOT_PERMITTED, 403)
    
    # 权限通过可以创建会议室
    try:
        room = await MeetingRoomService.create_room(db, room)
        app_logger.info(f"创建会议室：{room}, 用户ID：{current_user_id}")
    except IntegrityError as e:
        await db.rollback()
        app_logger.error(f"创建会议室失败：{e}, 用户ID：{current_user_id}")
        raise BizException(ErrorCode.DUPLICATE_ROOM_NUMBER, 400, f"会议室编号已存在：{room.room_number}")
    except Exception as e:
        await db.rollback()
        app_logger.error(f"创建会议室失败：{e}, 用户ID：{current_user_id}")
        raise BizException(ErrorCode.INTERNAL_ERROR, 500, "服务器内部错误")

    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="创建成功",
        data=room
    )


@router.get("", response_model=BaseResponse[List[MeetingRoomResponse]])
async def get_rooms(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """获取会议室列表"""
    rooms = await MeetingRoomService.get_rooms(db, is_active)
    app_logger.info(f"获取会议室列表：{rooms}")
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取成功",
        data=rooms
    )



@router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """删除会议室（仅管理员/人事部）"""
    current_user_id = current_user.id  # 此时会话正常，id已加载，不会触发额外查询

    if not current_user.is_superuser:
        user_departments = {
            role.department.name 
            for role in current_user.department_roles if role.department
        }
        if "人事部" not in user_departments:
            app_logger.error(f"用户 {current_user_id} 没有权限删除会议室")
            raise BizException(ErrorCode.NOT_PERMITTED, 403)
        
    success = await MeetingRoomService.delete_room(db, room_id)
    if not success:
        app_logger.error(f"删除会议室失败：{room_id}, 用户ID：{current_user_id}")
        raise BizException(ErrorCode.NOT_FOUND, 404)
    app_logger.info(f"删除会议室成功：{room_id}, 用户ID：{current_user_id}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="删除成功",
        data={
            "room_id": room_id
        }
    )


@router.patch("/{room_id}", response_model=BaseResponse[MeetingRoomResponse])
async def update_room(
    room_id: int,
    update_data: MeetingRoomUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """更新会议室信息（仅管理员/人事部）"""
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="还没实现",
        data=update_data
    )