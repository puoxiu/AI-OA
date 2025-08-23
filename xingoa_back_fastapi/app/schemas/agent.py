from pydantic import BaseModel

class StartChatRequest(BaseModel):
    """启动聊天请求模型"""
    title: str
    last_message: str



class ChatRequest(BaseModel):
    """聊天请求模型"""
    session_id: str = None
    message: str
