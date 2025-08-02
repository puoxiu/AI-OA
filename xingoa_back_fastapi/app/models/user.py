from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship


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
    is_staff = Column(Boolean, default=True)
    status = Column(Integer, default=UserStatusChoices.UNACTIVED)
    date_joined = Column(DATETIME(fsp=6), server_default=func.now())
    password_hashed = Column(String(64))
    last_login = Column(DateTime, nullable=True)

    is_superuser = Column(Boolean, default=False)

    leader_department = relationship("OADepartment", back_populates="leader", uselist=False, foreign_keys='OADepartment.leader_id', lazy="selectin")
    manager_departments = relationship("OADepartment", back_populates="manager", foreign_keys='OADepartment.manager_id', lazy="selectin")
    
    department_id = Column(Integer, ForeignKey('oa_department.id'), nullable=True)
    department = relationship("OADepartment", backref="staffs", foreign_keys=[department_id], lazy="selectin")

class OADepartment(Base):
    __tablename__ = "oa_department"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    intro = Column(String(200), nullable=True)

     # 每个部门只能有一个leader
    leader = relationship("OAUser", back_populates="leader_department", uselist=False, foreign_keys='OADepartment.leader_id', lazy="selectin")
    leader_id = Column(String(22), ForeignKey('oa_user.uid'), nullable=True)

    # 部门的上级
    manager = relationship("OAUser", back_populates="manager_departments", foreign_keys='OADepartment.manager_id', lazy="selectin")
    manager_id = Column(String(22), ForeignKey('oa_user.uid'), nullable=True)


