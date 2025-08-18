# AI-OA/xingoa_back_fastapi/app/schemas/absent.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class AbsentTypeRequest(BaseModel):
    pass


class AbsentTypeResponse(BaseModel):
    id: int
    name: str
    create_time: datetime

    class Config:
        from_attributes = True


class AbsentCreateResponse(BaseModel):
    """请假记录的响应模型，与 Absent 模型字段对应"""
    id: int
    title: str
    request_content: str
    status: int  # 对应 AbsentStatusChoices（如 1: 审核中, 2: 通过, 3: 拒绝）
    start_date: date
    end_date: date
    create_time: datetime
    response_content: Optional[str] = None  # 可能为 None（未审批时）
    requester_name: str
    requester_id: str
    responder_id: Optional[str]
    responder_name: Optional[str]
    absent_type_id: int
    absent_type_name: str

    class Config:
        from_attributes = True




class AbsentCreateRequest(BaseModel):
    title: str
    request_content: str
    absent_type_id: int
    start_date: date
    end_date: date

    @classmethod
    def validate_dates(cls, values):
        if values.get('start_date') and values.get('end_date'):
            if values['start_date'] >= values['end_date']:
                raise ValueError("开始日期必须早于结束日期")
        return values


class AbsentResponder(BaseModel):
    email: str
    username: str

class ProcessAbsentRequest(BaseModel):
    status: int = Field(..., description="处理状态（例如：1-未处理，2-通过，3-拒绝）")
    response_content: str = Field(..., min_length=1, max_length=500, description="处理意见")