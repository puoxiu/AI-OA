from pydantic import BaseModel


class AddStaffRequest(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        from_attributes = True