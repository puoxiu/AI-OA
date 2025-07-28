from pydantic import BaseModel, Field, EmailStr
from typing import Optional 
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



class StaffResponse(BaseModel):
    """员工响应模型（只包含需要返回的字段）"""
    uid: str
    username: str
    email: str
    phone: Optional[str]
    status: int
    date_joined: datetime  # 假设需要返回创建时间
    department: Optional[DepartmentResponse]  # 关联部门（用简化模型）

    class Config:
        from_attributes = True  # 允许从 ORM 对象映射（Pydantic v2，v1 用 orm_mode=True）
