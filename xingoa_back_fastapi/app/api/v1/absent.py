# AI-OA/xingoa_back_fastapi/app/api/v1/absent.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.absent import AbsentCreateResponse, AbsentCreateRequest, AbsentTypeResponse
from app.services.absent import AbsentService, AbsentTypeService
from deps.deps import get_db_session, get_current_user
from app.core.auth import AuthTokenHelper
from app.models.user import OAUser
from app.services.auth import UserService
from app.utils.absent import get_responder
from app.response_model import BaseResponse
from app.error import ErrorCode
from app.exceptions import BizException
from app.core.logging import app_logger

router = APIRouter(
    prefix="/api/v1/absent",
    tags=["考勤管理"]
)

from typing import List

@router.get("/type", response_model=BaseResponse[List[AbsentTypeResponse]])
async def get_absent_type(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """
    获取请假类型
    """
    absent_types = await AbsentTypeService.get_all_absent_type(db_session)
    
    app_logger.info(f"获取请假类型成功，用户：{current_user.uid}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取请假类型成功",
        data=absent_types
    )


@router.post("/add")
async def create_new_absent(
    absent: AbsentCreateRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """
    发出请假
    """
    responder = get_responder(current_user)

    new_absent = await AbsentService.create_absent(db_session, absent, current_user.uid, responder.uid)
    
    app_logger.info(f"请假成功，请假ID：{new_absent.id}，用户：{current_user.uid}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="请假成功",
        data=AbsentCreateResponse(
            id=new_absent.id,
            title=new_absent.title,
            request_content=new_absent.request_content,
            status=new_absent.status,
            start_date=new_absent.start_date,
            end_date=new_absent.end_date,
            create_time=new_absent.create_time,
            response_content=new_absent.response_content,
            requester_uid=new_absent.requester_uid,
            responder_uid=new_absent.responder_uid,
            absent_type_id=new_absent.absent_type_id,
        )
    )

# 查看自己的所有请求
@router.get("/my_absents", response_model=BaseResponse[list[AbsentCreateResponse]])
async def get_all_absents(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    my_absents = await AbsentService.get_all_absent_by_requester_uid(
        db_session=db_session,
        requester_uid=current_user.uid
    )
    
    app_logger.info(f"获取请假记录成功，用户：{current_user.uid}")
    
    # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取请假记录成功",
        data=my_absents
    )


# 查看下属的所有请假请求
@router.get("/my_all_staffs_absents", response_model=BaseResponse[list[AbsentCreateResponse]])
async def get_all_absents(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    my_absents = await AbsentService.get_all_absent_by_responder_uid(
        db_session=db_session,
        responder_uid=current_user.uid
    )
    
    app_logger.info(f"获取下属请假记录成功，用户：{current_user.uid}")
    
    # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取请假记录成功",
        data=my_absents
    )


# 查看还未处理的下属请假请求
@router.get("/my_staffs_absents", response_model=BaseResponse[list[AbsentCreateResponse]])
async def get_all_absents(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    my_absents = await AbsentService.get_all_absent_by_responder_uid_and_status(
        db_session=db_session,
        responder_uid=current_user.uid
    )
    
    app_logger.info(f"获取未处理下属请假记录成功，用户：{current_user.uid}")
    
    # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取请假记录成功",
        data=my_absents
    )

# 处理下属请假请求：必须status = 0；其它值则不可处理---即每个请假需求只处理一次
@router.patch("/my_staffs_absents")
async def process_new_absents(
    absent_id: int,
    status: int,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):    
    # 检查请假请求是否存在
    absent = await AbsentService.get_absent_by_id(db_session, absent_id)
    if not absent:
        raise BizException(ErrorCode.ABSENT_NOT_FOUND, 404)
    
    # 检查请假请求是否由当前用户处理
    if absent.responder_uid != current_user.uid:
        raise BizException(ErrorCode.NOT_PERMITTED, 403)
    
    # 检查请假请求状态是否为0
    if absent.status != 0:
        raise BizException(ErrorCode.ABSENT_ALREADY_PROCESSED, 400)
    
    # 更新请假请求状态
    await AbsentService.update_absent_status(db_session, absent_id, status)
    
    app_logger.info(f"处理请假请求成功，请假ID：{absent_id}，用户：{current_user.uid}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="处理请假请求成功",
        data=None
    )

