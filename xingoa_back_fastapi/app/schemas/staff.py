from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

from app.schemas.department import DepartmentResponse

class AddStaffRequest(BaseModel):
    realname: str = Field(max_length=20, description="真实姓名")
    email: EmailStr = Field(max_length=254, description="邮箱")
    password: str = Field(min_length=6, max_length=20, description="密码")
    phone: Optional[str] = Field(max_length=20, description="手机号")
    department_id: int = Field(description="部门ID")

    class Config:
        from_attributes = True

class DepartmentBriefResponse(BaseModel):
    """部门简要信息"""
    id: int
    name: str

class StaffResponse(BaseModel):
    """员工响应模型（只包含需要返回的字段）"""
    id: str
    username: str
    email: str
    phone: Optional[str]
    status: int
    date_joined: datetime
    departments: List[DepartmentBriefResponse]
    is_superuser: bool

    class Config:
        from_attributes = True  # 允许从 ORM 对象映射（Pydantic v2，v1 用 orm_mode=True）
