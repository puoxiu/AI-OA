# app/schemas/meeting_room.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from datetime import datetime, date, time, timezone
from app.schemas.user import OAUserResponse  # 复用用户模型
from app.schemas.department import DepartmentResponse  # 复用部门模型
# from app.schemas.pagination import Pagination

# 会议室基础信息
class MeetingRoomBase(BaseModel):
    room_number: str = Field(..., max_length=20, description="房间号")
    description: Optional[str] = None
    equipment: Optional[str] = Field(None, description="设备（逗号分隔）")
    capacity: int = Field(..., gt=0, description="容纳人数>0")

    # 这些信息不可为空
    

# 创建会议室
class MeetingRoomCreate(MeetingRoomBase):
    pass

# 更新会议室
class MeetingRoomUpdate(BaseModel):
    room_number: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    equipment: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

# 会议室响应
class MeetingRoomResponse(MeetingRoomBase):
    id: int
    is_active: bool
    create_time: datetime
    
    class Config:
        from_attributes = True
