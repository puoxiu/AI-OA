
# app/models/meeting_room.py

from sqlalchemy import Column, Integer, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from sqlalchemy import Table, func

from db.database import Base
from app.models.user import OAUser, OADepartment





class MeetingRoom(Base):
    """会议室模型"""
    __tablename__ = "meeting_room"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number = Column(String(20), unique=True, nullable=False, comment="房间号")
    description = Column(Text, nullable=False, comment="描述")
    equipment = Column(String(255), nullable=False, comment="设备（逗号分隔，如：投影仪,白板）")
    capacity = Column(Integer, nullable=False, comment="容纳人数")
    is_active = Column(Boolean, default=True, comment="是否可用")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    # 关联预订记录
    bookings = relationship("MeetingBooking", back_populates="room", lazy="selectin")


class MeetingBooking(Base):
    """会议室预订记录表"""
    __tablename__ = "meeting_booking"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    title = Column(String(100), nullable=False, comment="会议主题")
    description = Column(Text, comment="会议内容/备注")

    room_id = Column(Integer, ForeignKey("meeting_room.id"), nullable=False, comment="会议室ID")
    booker_id = Column(String(22), ForeignKey("oa_user.uid"), nullable=False, comment="预订人ID")

    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")

    is_approved = Column(Boolean, default=True, comment="是否已审批, 默认直接通过")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系映射
    room = relationship("MeetingRoom", back_populates="bookings", lazy="selectin")
    booker = relationship("OAUser", backref="booked_meetings", lazy="selectin")
