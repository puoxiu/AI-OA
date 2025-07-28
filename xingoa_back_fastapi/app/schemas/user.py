from pydantic import BaseModel
from pydantic.functional_validators import field_validator


class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict



class ResetPwdRequest(BaseModel):
    email: str
    verify_code: str
    new_pwd1: str
    new_pwd2: str

    @field_validator('verify_code')
    @classmethod
    def validate_verify_code(cls, v, info):
        email = info.data.get('email')
        if not email:
            raise ValueError("未提供邮箱信息")
        
        # 从 Redis 中获取存储的验证码
        # stored_code = redis_client.get(email)
        # if not stored_code or stored_code.decode() != v:
        #     raise ValueError("验证码无效或已过期")
        
        # 目前固定验证码
        stored_code = "123123"
        if stored_code != v:
            raise ValueError("验证码无效或已过期")
    
    @field_validator('new_pwd2')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_pwd1' in info.data and v != info.data['new_pwd1']:
            raise ValueError("两个新密码不一致！")
        return v

class ResetPwdResponse(BaseModel):
    message: str


class OAUserResponse(BaseModel):
    uid: str
    username: str
    email: str
    # 可以根据实际需求添加更多字段

    class Config:
        from_attributes = True