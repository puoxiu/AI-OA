from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.inform import InformsResponse, InformCreateRequest
from app.services.inform import InformService
from deps.deps import get_db_session, get_current_user

from app.models.user import OAUser

from app.response_model import BaseResponse
from app.error import ErrorCode
from app.core.logging import app_logger
from app.exceptions import BizException
from app.error import ErrorCode

router = APIRouter(
    prefix="/api/v1/inform",
    tags=["通知管理"]
)

# 查询所有可见的通知
@router.get("/all", response_model=BaseResponse[List[InformsResponse]])
async def get_informs(db_session: AsyncSession = Depends(get_db_session), current_user: OAUser = Depends(get_current_user)):
    try:
        informs = await InformService.get_informs(db_session, current_user)
    except Exception as e:
        app_logger.error(f"获取通知信息失败，用户：{current_user.id}，错误信息：{e}")
        raise BizException(ErrorCode.SERVER_ERROR, 500, "服务端错误")
    
    app_logger.info(f"获取通知信息成功，用户：{current_user.id}，通知数量：{len(informs)}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取通知信息成功",
        data=informs
    )

# 创建新的通知
@router.post("/create_inform", response_model=BaseResponse[dict])
async def create_inform(
    inform: InformCreateRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    try:
        new_inform = await InformService.create_inform(db_session, inform.title, inform.content, inform.public, current_user)
    except Exception as e:
        app_logger.error(f"创建通知失败，用户：{current_user.id}，错误信息：{e}")
        raise BizException(ErrorCode.SERVER_ERROR, 500, "服务端错误")
    
    app_logger.info(f"创建通知成功，通知ID：{new_inform.id}，用户：{current_user.id}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="创建通知成功",
        data={
            "id": new_inform.id,
            "title": new_inform.title,
            "content": new_inform.content,
            "public": new_inform.public,
            "author_id": new_inform.author_id,
            "create_time": new_inform.create_time,
        }
    )

# 读取通知内容并设置为已读
@router.get("/{inform_id}", response_model=BaseResponse[dict])
async def read_inform(
    inform_id: int,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    try:
        # 1. 查询通知
        inform = await InformService.get_inform_by_id(db_session, current_user, inform_id)
        
        # 2. 检查通知是否存在
        if not inform:
            app_logger.warning(f"通知不存在，通知ID：{inform_id}，用户：{current_user.id}")
            raise BizException(ErrorCode.INFORM_NOT_FOUND, 404, "通知不存在")
        
        # 3. 检查是否已读，未读则创建阅读记录
        read_record = await InformService.get_inform_read_record_by_id(db_session, current_user, inform_id)
        if not read_record:
            await InformService.create_inform_read_record(db_session, current_user, inform_id)
            app_logger.info(f"创建通知阅读记录成功，通知ID：{inform_id}，用户：{current_user.id}")
        
        # 4. 返回通知内容
        return BaseResponse(
            code=ErrorCode.SUCCESS,
            msg="读取通知成功",
            data={
                "id": inform.id,
                "title": inform.title,
                "content": inform.content,
                "public": inform.public,
                "author_id": inform.author_id,
                "create_time": inform.create_time,
                "author": {
                    "id": inform.author.id,
                    "username": inform.author.username,
                    "email": inform.author.email,
                },
                "is_read": bool(read_record)
            }
        )

    except Exception as e:
        app_logger.error(f"获取通知信息失败，用户：{current_user.id}，通知ID：{inform_id}，错误信息：{e}")
        raise BizException(ErrorCode.SERVER_ERROR, 500, "服务端错误")
