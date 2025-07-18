# AI-OA/xingoa_back_fastapi/app/schemas/absent.py
from pydantic import BaseModel
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
    response_content: Optional[str]  # 可能为 None（未审批时）
    requester_uid: str
    responder_uid: Optional[str]
    absent_type_id: int

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




class AbsentUpdate(BaseModel):
    status: int
    response_content: Optional[str]