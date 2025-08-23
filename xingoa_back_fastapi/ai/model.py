from pydantic import BaseModel
from typing import Dict
from dataclasses import dataclass

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str
    timestamp: float




@dataclass
class AiRole:
    name: str  # 角色名称
    icon: str  # 角色图标
    prompt: str  # 角色提示词

AI_ROLES: Dict[str, AiRole] = {
    "assistant": AiRole(
        name="智能助手",
        icon="🤖",
        prompt="你是一个友善、专业的AI助手，能够帮助用户解答各种问题。请保持礼貌和耐心。"
    ),
    "teacher": AiRole(
        name="AI老师",
        icon="👨‍🏫",
        prompt="你是一位经验丰富的老师，擅长用简单易懂的方式解释复杂概念..."
    ),
    "programmer": AiRole(
        name="编程专家",
        icon="👨‍💻",
        prompt="你是一位资深的程序员，精通多种编程语言和技术栈..."
    )
}