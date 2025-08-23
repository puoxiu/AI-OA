import uuid
from ai.ai_logger import ai_logger
from ai.ai_config import ai_settings
from ai.model import ChatMessage
import json
from ai.deps import redis_client
from typing import List, Dict, Any



class Session:
    @staticmethod
    def generate_session_id() -> str:
        """生成唯一的会话ID"""
        session_id = str(uuid.uuid4())
        ai_logger.info(f"生成新会话ID: {session_id}")
        return session_id

    @staticmethod
    def get_conversation_key(user_id: str, session_id: str) -> str:
        """获取对话在Redis中的键名"""
        return f"conversation:{user_id}:{session_id}"

    @staticmethod
    def get_user_sessions_key(user_id: str) -> str:
        """获取用户会话列表在Redis中的键名"""
        return f"user_sessions:{user_id}"

    @staticmethod
    async def update_session_list(user_id: str, session_id: str, last_message: ChatMessage, title: str = None):
        """更新/添加用户会话"""
        sessions_key = Session.get_user_sessions_key(user_id)

        existing_data_str = redis_client.hget(sessions_key, session_id)

        if existing_data_str:
            session_info = json.loads(existing_data_str)
        else:
            ai_logger.info(f"创建新会话 - 用户: {user_id}, 会话: {session_id[:8]}..., 标题: {title}")
            session_info = {
                "session_id": session_id,
                "title": title,
            }

        session_info["last_message"] = last_message.content[:ai_settings.MESSAGE_MAX_LENGTH] + "..." if len(last_message.content) > ai_settings.MESSAGE_MAX_LENGTH else last_message.content
        session_info["last_timestamp"] = last_message.timestamp

        redis_client.hset(sessions_key, session_id, json.dumps(session_info))
        redis_client.expire(sessions_key, ai_settings.SESSION_EXPIRE_TIME)

    @staticmethod
    async def delete_session(user_id: str, session_id: str) -> bool:
        """
        删除用户的指定会话（包括会话列表记录和聊天历史）
        :param user_id: 用户ID
        :param session_id: 要删除的会话ID
        :return: 删除成功返回 True，会话不存在返回 False
        """
        try:
            # 1. 定义 Redis 键（复用已有的键生成方法，确保一致性）
            sessions_key = Session.get_user_sessions_key(user_id)  # 用户会话列表键
            conversation_key = Session.get_conversation_key(user_id, session_id)  # 会话聊天历史键

            # 2. 先检查会话是否存在（避免删除不存在的资源）
            existing_session = redis_client.hget(sessions_key, session_id)
            if not existing_session:
                ai_logger.warning(f"会话不存在，无需删除 - 用户: {user_id}, 会话: {session_id[:8]}...")
                return False  # 会话不存在，返回 False 标识

            # 3. 删除会话列表中的目标会话记录（从 hash 中删除指定 field）
            redis_client.hdel(sessions_key, session_id)
            ai_logger.info(f"已删除会话列表中的记录 - 用户: {user_id}, 会话: {session_id[:8]}...")

            # 4. 删除该会话对应的完整聊天历史（删除整个 list 键）
            redis_client.delete(conversation_key)
            ai_logger.info(f"已删除会话的聊天历史 - 用户: {user_id}, 会话: {session_id[:8]}...")

            # 5. 可选：如果用户会话列表为空，可删除整个会话列表键（减少 Redis 冗余）
            remaining_sessions = redis_client.hlen(sessions_key)
            if remaining_sessions == 0:
                redis_client.delete(sessions_key)
                ai_logger.info(f"用户会话列表已空，删除空列表键 - 用户: {user_id}")

            return True

        except Exception as e:
            ai_logger.error(f"删除会话失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {str(e)}")
            raise  


    @staticmethod
    async def save_message_to_redis(user_id: str, session_id: str, message: ChatMessage, title: str = None):
        """将消息保存到Redis"""
        try:
            message_data = {
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp,
                "image_data": getattr(message, 'image_data', None),
                "image_type": getattr(message, 'image_type', None)
            }
            # 使用Redis存储
            conversation_key =  Session.get_conversation_key(user_id, session_id)

            # 将消息添加到对话历史
            redis_client.lpush(conversation_key, json.dumps(message_data))

            # 设置过期时间
            redis_client.expire(conversation_key, ai_settings.MESSAGE_EXPIRE_TIME)

            # 更新用户会话列表
            await Session.update_session_list(user_id, session_id, message, title)
            ai_logger.info(f"消息已保存到Redis - 用户: {user_id}, 会话: {session_id[:8]}..., 角色: {message.role}, 内容长度: {len(message.content)}")

        except Exception as e:
            ai_logger.error(f"保存消息失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {e}")
            raise

    @staticmethod
    async def get_conversation_history(user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """从Redis获取对话历史"""
        try:
            # 从Redis获取
            conversation_key =  Session.get_conversation_key(user_id, session_id)
            messages = redis_client.lrange(conversation_key, 0, -1)

            # 反转消息顺序（Redis中是倒序存储的）
            messages.reverse()

            history = [json.loads(msg) for msg in messages]
            ai_logger.info(f"从Redis获取对话历史 - 用户: {user_id}, 会话: {session_id[:8]}..., 消息数量: {len(history)}")
            return history

        except Exception as e:
            ai_logger.error(f"获取对话历史失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {e}")
            return []
        
    @staticmethod
    async def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
        """从 Redis 获取用户会话列表"""
        try:
            sessions_key = Session.get_user_sessions_key(user_id)
            raw_sessions = redis_client.hgetall(sessions_key)

            sessions = []
            for session_id, session_info in raw_sessions.items():
                try:
                    # 先 decode 再 loads
                    info = json.loads(session_info.decode("utf-8"))
                    sessions.append(info)
                except Exception as inner_e:
                    ai_logger.error(f"解析会话信息失败 - 用户: {user_id}, session_id: {session_id}, 错误: {inner_e}")

            # 按最后时间排序（最新的在最前）
            sessions.sort(key=lambda x: x.get("last_timestamp", ""), reverse=True)

            return sessions

        except Exception as e:
            ai_logger.error(f"获取用户会话列表失败 - 用户: {user_id}, 错误: {e}")
            return []