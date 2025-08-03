# app/schemas/meeting_booking.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.meeting_room import MeetingRoomResponse
from app.schemas.user import OAUserResponse

class MeetingBookingBase(BaseModel):
    title: str = Field(..., max_length=100, description="会议主题")
    description: Optional[str] = Field(None, description="会议内容/备注")
    room_id: int = Field(..., description="会议室ID")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v

class MeetingBookingCreate(MeetingBookingBase):
    pass


class MeetingBookingResponse(MeetingBookingBase):
    id: int
    booker_id: str
    is_approved: bool
    create_time: datetime
    booker: OAUserResponse
    room: MeetingRoomResponse

    class Config:
        from_attributes = True