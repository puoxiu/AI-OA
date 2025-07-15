from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import DATETIME

from db.database import Base


class UserStatusChoices:
    ACTIVED = 1
    UNACTIVED = 2
    LOCKED = 3


class OAUser(Base):
    __tablename__ = "oa_user"
    uid = Column(String(22), primary_key=True)
    username = Column(String(150), unique=True)
    email = Column(String(254), unique=True)
    phone = Column(String(20), nullable=True)
    is_staff = Column(Integer, default=1)
    status = Column(Integer, default=UserStatusChoices.UNACTIVED)
    date_joined = Column(DATETIME(fsp=6), server_default=func.now())
    password = Column(String(128))
    last_login = Column(DateTime, nullable=True)

