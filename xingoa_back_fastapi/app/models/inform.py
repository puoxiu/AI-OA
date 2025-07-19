from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint
from db.database import Base
from .user import OAUser, OADepartment

class Inform(Base):
    __tablename__ = "inform"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)
    create_time = Column(DateTime, server_default=func.now())
    # 如果设置为true 则表示全部职工可见
    public = Column(Boolean, default=False)
    author_id = Column(String(22), ForeignKey("oa_user.uid"))
    author = relationship("OAUser", backref="informs")
    departments = relationship("OADepartment", secondary="inform_department", backref="informs")

    @property
    def author_name(self):
        # 假设 OAUser 模型中用户名称字段为 username（根据实际字段名修改）
        return self.author.username if self.author else "未知用户"


class InformRead(Base):
    __tablename__ = "inform_read"

    id = Column(Integer, primary_key=True, autoincrement=True)
    inform_id = Column(Integer, ForeignKey("inform.id"), nullable=False)
    user_id = Column(String(22), ForeignKey("oa_user.uid"), nullable=False)
    read_time = Column(DateTime, server_default=func.now())

    inform = relationship("Inform", backref="reads")
    user = relationship("OAUser", backref="reads")

    __table_args__ = (
        UniqueConstraint('inform_id', 'user_id', name='_inform_user_uc'),
    )


class InformDepartment(Base):
    """
    记录通知是哪些部门可见
    """
    __tablename__ = "inform_department"

    inform_id = Column(Integer, ForeignKey("inform.id"), primary_key=True)
    department_id = Column(Integer, ForeignKey("oa_department.id"), primary_key=True)