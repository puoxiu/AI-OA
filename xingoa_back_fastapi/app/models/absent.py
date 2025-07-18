# AI-OA/xingoa_back_fastapi/app/models/absent.py
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
from app.models.user import OAUser



class AbsentType(Base):
    __tablename__ = "absent_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    create_time = Column(DateTime, server_default=func.now())
    absents = relationship("Absent", back_populates="absent_type")


class AbsentStatusChoices:
    # 审批中
    AUDITING = 1
    # 审核通过
    PASS = 2
    # 审核拒绝
    REJECT = 3

class Absent(Base):
    __tablename__ = "absent"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    request_content = Column(Text)
    status = Column(Integer, default=AbsentStatusChoices.AUDITING)
    start_date = Column(Date)
    end_date = Column(Date)
    create_time = Column(DateTime, server_default=func.now())
    response_content = Column(Text, nullable=True)

    requester_uid = Column(String(22), ForeignKey('oa_user.uid'))
    requester = relationship("OAUser", backref="my_absents", foreign_keys=[requester_uid])

    responder_uid = Column(String(22), ForeignKey('oa_user.uid'), nullable=True)
    responder = relationship("OAUser", backref="sub_absents", foreign_keys=[responder_uid])

    absent_type_id = Column(Integer, ForeignKey('absent_type.id'))
    absent_type = relationship("AbsentType", back_populates="absents")
