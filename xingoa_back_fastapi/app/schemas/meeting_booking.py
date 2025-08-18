# app/schemas/meeting_booking.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.meeting_room import MeetingRoomResponse
from app.schemas.user import OAUserResponse

class MeetingBookingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="会议主题")
    description: Optional[str] = Field(None, max_length=500, description="会议内容/备注")
    room_id: int = Field(..., description="会议室ID")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")



class MeetingBookingCreate(MeetingBookingBase):
    """创建预订时的请求模型"""
    pass

class MeetingBookingResponse(MeetingBookingBase):
    """预订成功后的响应模型"""
    id: int
    create_time: datetime
    is_approved: bool
    booker_id: str
    
    class Config:
        orm_mode = True
