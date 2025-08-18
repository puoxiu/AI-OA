from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import String, Integer, DateTime
from datetime import datetime


from db.database import Base
# from app.models.inform import Inform, InformRead
# from app.models.meeting_room import MeetingBooking

class UserStatusChoices:
    ACTIVED = 1
    UNACTIVED = 2
    LOCKED = 3


class DepartmentRoleChoices:
    LEADER = "leader"   # 部门领导
    MANAGER = "manager" # 部门上级
    MEMBER = "member"   # 部门成员


class DepartmentUserRole(Base):
    """
    部门用户角色表：
    - 一个用户可以在多个部门
    - 同一个用户在一个部门内只能有一个角色
    """
    __tablename__ = "oa_department_user_role"
    __table_args__ = (
        UniqueConstraint("department_id", "user_id", name="uq_department_user"),  # 避免重复
        # 依赖关系
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(20), default=DepartmentRoleChoices.MEMBER)

    department_id: Mapped[int] = mapped_column(ForeignKey("oa_department.id"), nullable=False)
    department: Mapped["OADepartment"] = relationship("OADepartment", back_populates="user_roles", lazy="selectin")
    
    user_id: Mapped[str] = mapped_column(ForeignKey("oa_user.id"), nullable=False)
    user: Mapped["OAUser"] = relationship("OAUser", back_populates="department_roles", lazy="selectin")


class OADepartment(Base):
    __tablename__ = "oa_department"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    intro: Mapped[str] = mapped_column(String(254), nullable=False)

    # 部门与用户角色的关联
    user_roles: Mapped[list["DepartmentUserRole"]] = relationship(
        "DepartmentUserRole",
        back_populates="department",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    # 部门关联的通知
    informs: Mapped[list["Inform"]] = relationship("Inform", secondary="inform_department", back_populates="departments", lazy="selectin")

class OAUser(Base):
    __tablename__ = "oa_user"

    id: Mapped[str] = mapped_column(String(22), primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)
    password_hashed: Mapped[str] = mapped_column(String(64), nullable=False)
    is_staff: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    status: Mapped[int] = mapped_column(Integer, default=UserStatusChoices.ACTIVED)
    date_joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # 用户与部门角色的关联
    department_roles: Mapped[list["DepartmentUserRole"]] = relationship(
        "DepartmentUserRole",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    # 用户发布的通知
    informs: Mapped[list["Inform"]] = relationship("Inform", back_populates="author", lazy="selectin")

    # 用户阅读记录
    read_records: Mapped[list["InformRead"]] = relationship("InformRead", back_populates="user", lazy="selectin")

    # 用户预订的会议
    booked_meetings: Mapped[list["MeetingBooking"]] = relationship("MeetingBooking", back_populates="booker", lazy="selectin")