# AI-OA/xingoa_back_fastapi/app/models/absent.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Text, Date, DateTime
from datetime import datetime, date

class AbsentType(Base):
    __tablename__ = "absent_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20))
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    absents = relationship("Absent", back_populates="absent_type", lazy="selectin")


class AbsentStatusChoices:
    # 待审批
    AUDITING = 1
    # 审核通过
    PASS = 2
    # 审核拒绝
    REJECT = 3

class Absent(Base):
    __tablename__ = "absent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    request_content: Mapped[str] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer, default=AbsentStatusChoices.AUDITING)
    
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    response_content: Mapped[str] = mapped_column(Text, nullable=True)

    # 请假人
    requester_id: Mapped[str] = mapped_column(String(22), ForeignKey('oa_user.id'))
    requester = relationship("OAUser", backref="my_absents", foreign_keys=[requester_id], lazy="selectin")

    # 审批人
    responder_id: Mapped[str] = mapped_column(String(22), ForeignKey('oa_user.id'), nullable=True)
    responder = relationship("OAUser", backref="sub_absents", foreign_keys=[responder_id], lazy="selectin")

    # 请假类型
    absent_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('absent_type.id'))
    absent_type = relationship("AbsentType", back_populates="absents", lazy="selectin")
