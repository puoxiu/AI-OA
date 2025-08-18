
# app/models/meeting_room.py

from sqlalchemy import Integer, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from sqlalchemy import func

from db.database import Base
from app.models.user import OAUser


class MeetingRoom(Base):
    """会议室模型"""
    __tablename__ = "meeting_room"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="房间号")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="描述")
    equipment: Mapped[str] = mapped_column(String(255), nullable=False, comment="设备（逗号分隔，如：投影仪,白板）")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, comment="容纳人数")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可用")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    # 关联预订记录
    bookings: Mapped[list["MeetingBooking"]] = relationship("MeetingBooking", back_populates="room", lazy="selectin")


class MeetingBooking(Base):
    """会议室预订记录表"""
    __tablename__ = "meeting_booking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="会议主题")
    description: Mapped[str] = mapped_column(Text, comment="会议内容/备注")

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="开始时间")
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="结束时间")

    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否已审批, 默认直接通过")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系映射
    # 会议室关联
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("meeting_room.id"), nullable=False, comment="会议室ID")
    room: Mapped["MeetingRoom"] = relationship("MeetingRoom", back_populates="bookings", lazy="selectin")

    # 预订人关联
    booker_id: Mapped[str] = mapped_column(String(22), ForeignKey("oa_user.id"), nullable=False, comment="预订人ID")
    booker: Mapped["OAUser"] = relationship("OAUser", back_populates="booked_meetings", lazy="selectin")
