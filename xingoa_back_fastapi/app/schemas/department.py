
from pydantic import BaseModel

from app.schemas.user import OAUserResponse

class DepartmentResponse(BaseModel):
    id: int
    name: str
    intro: str
    leader: OAUserResponse | None
    manager: OAUserResponse | None


    class Config:
        from_attributes = True



