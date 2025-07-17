# AI-OA/xingoa_back_fastapi/app/schemas/absent.py
from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserSerializer

class AbsentTypeSerializer(BaseModel):
    id: int
    name: str
    create_time: Optional[str]

    class Config:
        orm_mode = True

class AbsentCreateResponse(BaseModel):
    id: int
    title: str
    request_content: str
    status: int
    start_date: str
    end_date: str
    create_time: Optional[str]
    response_content: Optional[str]
    requester: UserSerializer
    responder: Optional[UserSerializer]
    absent_type: AbsentTypeSerializer

    class Config:
        orm_mode = True

class AbsentCreateRequest(BaseModel):
    title: str
    request_content: str
    absent_type_id: int
    start_date: str
    end_date: str

class AbsentUpdate(BaseModel):
    status: int
    response_content: Optional[str]