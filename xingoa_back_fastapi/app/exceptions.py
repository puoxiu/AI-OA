# exceptions.py
from fastapi import HTTPException
from .error import ERROR_MESSAGES

class BizException(HTTPException):
    def __init__(self, code: int, status_code: int = 400):
        detail = ERROR_MESSAGES.get(code, "未知错误")
        super().__init__(status_code=status_code, detail={"code": code, "msg": detail})

