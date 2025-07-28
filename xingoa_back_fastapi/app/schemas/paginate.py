from pydantic import BaseModel
from typing import List, Generic, TypeVar

T = TypeVar('T')  # 泛型类型

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应通用模型"""
    total: int
    page: int
    page_size: int
    items: List[T]  # 泛型列表，可接收任意类型的响应模型