from pydantic import BaseModel, Field, EmailStr
from typing import Optional 

class AddStaffRequest(BaseModel):
    realname: str = Field(max_length=20, description="真实姓名")
    email: EmailStr = Field(max_length=254, description="邮箱")
    password: str = Field(min_length=6, max_length=20, description="密码")
    phone: Optional[str] = Field(max_length=20, description="手机号")
    department_id: int = Field(description="部门ID")

    class Config:
        from_attributes = True