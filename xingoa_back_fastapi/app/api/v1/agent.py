from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser
from app.core.logging import app_logger
from app.response_model import BaseResponse
from app.error import ErrorCode
from app.exceptions import BizException
from app.schemas.agent import StartChatRequest, ChatRequest

from ai.model import ChatMessage
from ai.session import Session
from ai.call_llm import stream_llm


router = APIRouter(
    prefix="/api/v1/ai",
    tags=["用户对话"]
)

@router.get("/chat/sessions")
async def get_chat_sessions(
    current_user: OAUser = Depends(get_current_user)
):
    """
    获取用户已有会话列表
    """
    app_logger.info(f"获取用户已有会话列表 - 用户: {current_user.id}")
    sessions = await Session.get_user_sessions(current_user.id)

    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="会话获取成功",
        data={
            "sessions": sessions
        }
    )


@router.get("/chat/history")
async def get_chat_history(
    session_id: str = Query(..., description="会话ID"),
    current_user: OAUser = Depends(get_current_user)
):
    """
    获取用户某个会话的对话历史
    """
    app_logger.info(f"获取用户某个会话的对话历史 - 用户: {current_user.id}, 会话: {session_id[:8]}...")
    
    try:
        user_id = current_user.id
        history = await Session.get_conversation_history(user_id, session_id)
        app_logger.info(f"聊天历史获取成功 - 用户: {user_id}, 会话: {session_id[:8]}..., 消息数: {len(history)}")

        return BaseResponse(
            code=ErrorCode.SUCCESS,
            msg="聊天历史获取成功",
            data={
                "history": history,
                "session_id": session_id,
                "total": len(history)
            }
        )
    except Exception as e:
        app_logger.error(f"获取用户某个会话的聊天历史失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {e}")

        raise BizException(ErrorCode.SERVER_ERROR, 500, "服务端错误, 请联系管理员或者稍后再试!")


@router.post("/chat/start")
async def start_chat(
    request: StartChatRequest,
    current_user: OAUser = Depends(get_current_user)
):
    """
    启动一个新的对话会话
    """
    session_id = Session.generate_session_id()
    last_message = ChatMessage(role="assistant", content=request.last_message, timestamp=datetime.now().timestamp())

    await Session.save_message_to_redis(current_user.id, session_id, last_message, request.title)

    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="会话启动成功",
        data={
            "session_id": session_id,
            "title": request.title,
            "last_message": request.last_message,
            "last_timestamp": last_message.timestamp,
        }
    )

@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: OAUser = Depends(get_current_user)
):
    """
    删除一个对话会话
    """
    app_logger.info(f"收到会话删除请求 - 用户: {current_user.id}, 会话: {session_id[:8]}...")
    
    try:
        # 1. 调用 Session 类的删除方法，传入当前用户ID和目标会话ID
        delete_success = await Session.delete_session(
            user_id=str(current_user.id),
            session_id=session_id
        )

        # 2. 根据删除结果返回不同响应
        if delete_success:
            return BaseResponse(
                code=ErrorCode.SUCCESS,
                msg="会话删除成功",
                data={"session_id": session_id}
            )
        else:
            # 会话不存在，返回 404 状态码
            raise BizException(
                error_code=ErrorCode.NOT_FOUND,
                status_code=404,
                message=f"会话不存在或已删除 - session_id: {session_id[:8]}..."
            )

    except BizException as e:
        app_logger.warning(f"会话删除业务异常 - 用户: {current_user.id}, 会话: {session_id[:8]}..., 原因: {e.message}")
        raise

    except Exception as e:
        app_logger.error(
            f"会话删除服务端异常 - 用户: {current_user.id}, 会话: {session_id[:8]}..., 错误: {str(e)}",
            exc_info=True
        )
        raise BizException(
            error_code=ErrorCode.SERVER_ERROR,
            status_code=500,
            message="会话删除失败，请稍后重试"
        )

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: OAUser = Depends(get_current_user)
):
    """
    流式对话接口
    """
    role = "user"
    user_message = ChatMessage(
        role=role,
        content=request.message,
        timestamp=datetime.now().timestamp()
    )
    await Session.save_message_to_redis(current_user.id, request.session_id, user_message)


    async def event_generator():
        try:
            final_answer = ""
            async for chunk in stream_llm(prompt=request.message):
                # 2. 把流式结果返回给前端
                yield f"data: {chunk}\n\n"
                final_answer += chunk

            # 3. 保存助手的完整回复
            assistant_message = ChatMessage(
                role="assistant",
                content=final_answer,
                timestamp=datetime.now().timestamp()
            )
            await Session.save_message_to_redis(current_user.id, request.session_id, assistant_message)

            # 4. 发送完成信号
            yield "event: done\ndata: [DONE]\n\n"
        except Exception as e:
            app_logger.error(f"流式对话错误 - 用户: {current_user.id}, 会话: {request.session_id}, 错误: {e}")
            yield f"event: error\ndata: 服务端错误: {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")