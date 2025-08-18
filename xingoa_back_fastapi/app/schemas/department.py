
from pydantic import BaseModel
from typing import Optional

from app.schemas.user import OAUserResponse

# class DepartmentResponse(BaseModel):
#     id: int
#     name: str
#     leader: OAUserResponse | None
#     manager: OAUserResponse | None


#     class Config:
#         from_attributes = True

class DepartmentResponse(BaseModel):
    """部门响应模型（排除反向关联的 staffs，避免循环）"""
    id: int
    name: str
    leader: dict | None
    manager: dict | None

    class Config:
        from_attributes = True  # 允许从 ORM 对象映射

