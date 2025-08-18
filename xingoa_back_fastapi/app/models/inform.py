from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column  
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint
from datetime import datetime

from db.database import Base
from .user import OAUser, OADepartment

class InformDepartment(Base):
    """
    记录通知是哪些部门可见--多对多
    """
    __tablename__ = "inform_department"

    inform_id = Column(Integer, ForeignKey("inform.id"), primary_key=True)
    department_id = Column(Integer, ForeignKey("oa_department.id"), primary_key=True)


class Inform(Base):
    __tablename__ = "inform"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    # 如果设置为true 则表示全部职工可见; 否则表示仅部门可见
    public: Mapped[bool] = mapped_column(Boolean, default=False)
    # 该通知的作者
    author_id: Mapped[str] = mapped_column(String(22), ForeignKey("oa_user.id"), nullable=False)
    author: Mapped[OAUser] = relationship("OAUser", back_populates="informs", lazy="selectin")
    
    # 通知的可见部门
    departments: Mapped[list[OADepartment]] = relationship("OADepartment", secondary="inform_department", back_populates="informs", lazy="selectin")
    # 通知的阅读记录
    read_records: Mapped[list["InformRead"]] = relationship("InformRead", back_populates="inform", lazy="selectin")

class InformRead(Base):
    __tablename__ = "inform_read"
    
    inform_id: Mapped[int] = mapped_column(Integer, ForeignKey("inform.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(22), ForeignKey("oa_user.id"), primary_key=True)
    read_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    inform: Mapped[Inform] = relationship("Inform", back_populates="read_records", lazy="selectin")
    user: Mapped[OAUser] = relationship("OAUser", back_populates="read_records", lazy="selectin")
