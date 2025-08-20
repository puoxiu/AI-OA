from pydantic import BaseModel
from datetime import datetime

# 通知列表响应：只需返回通知的简要信息
class InformsResponse(BaseModel):
    id: int
    title: str
    author_id: str
    author_name: str
    author_department_name: str
    is_read: bool = False
    is_public: bool = False
    create_time: datetime

    class Config:
        from_attributes = True

# 通知详情响应：返回某条通知的详细信息，就是给用户看的内容
class InformDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: str
    author_name: str
    create_time: datetime

    class Config:
        # 作用: 从数据库模型转换为 Pydantic 模型时，自动映射字段
        from_attributes = True


# 通知创建请求：用户创建通知时需要传递的参数
class InformCreateRequest(BaseModel):
    title: str
    content: str
    # public: bool = True
    department_ids: list[int] = []  # 指定可见的部门id，如果传入含有id=0 则说明所有部门可见

    class Config:
        # 作用: 从数据库模型转换为 Pydantic 模型时，自动映射字段
        from_attributes = True
