# AI-OA/xingoa_back_fastapi/app/api/v1/absent.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.absent import AbsentCreateResponse, AbsentCreateRequest, AbsentTypeResponse, AbsentResponder
from app.services.absent import AbsentService, AbsentTypeService
from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser
from app.response_model import BaseResponse
from app.error import ErrorCode
from app.exceptions import BizException
from app.core.logging import app_logger
from app.schemas.paginate import PaginatedResponse
from app.schemas.absent import ProcessAbsentRequest

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
    
    app_logger.info(f"获取请假类型成功，用户：{current_user.id}")
    
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
    try:
        responder = await AbsentService.get_absent_responder(db_session, current_user)
    except BizException as e:
        app_logger.error(f"获取审批人失败，用户：{current_user.id}，错误：{e}")
        raise BizException(ErrorCode.SERVER_ERROR, 500)
    

    new_absent = await AbsentService.create_absent(db_session, absent, current_user, responder)
    
    app_logger.info(f"请假成功，请假ID：{new_absent.id}，用户：{current_user.id}")
    
    # todo
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="请假成功",
        data= {
            "id": new_absent.id,
            "status": new_absent.status,
            "responder_id": new_absent.responder_id,
            "responder_name": new_absent.responder.username,
        }
    )

# 查看自己的所有请求
@router.get("/my_absents", response_model=BaseResponse[PaginatedResponse[AbsentCreateResponse]])
async def get_all_absents(
    page: int = 1,
    page_size: int = 10,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    my_absents, total_count = await AbsentService.get_all_absent_by_requester_id(
        db_session=db_session,
        requester_id=current_user.id,
        page=page,
        page_size=page_size
    )
    total_page = (total_count + page_size - 1) // page_size

    # 转换为 Pydantic 模型
    processed_absents = []
    for absent in my_absents:
        processed_absent = {
            "id": absent.id,
            "title": absent.title,
            "request_content": absent.request_content,
            "status": absent.status,
            "start_date": absent.start_date,
            "end_date": absent.end_date,
            "create_time": absent.create_time,
            "response_content": absent.response_content,
            "requester_id": absent.requester_id,
            "responder_id": absent.responder_id,
            "absent_type_id": absent.absent_type_id,
            "requester_name": absent.requester.username if absent.requester else "",
            "responder_name": absent.responder.username if absent.responder else None,
            "absent_type_name": absent.absent_type.name if absent.absent_type else ""
        }
        processed_absents.append(processed_absent)

    app_logger.info(f"获取请假记录成功，用户：{current_user.id}，总记录数：{total_count}，总页数：{total_page}")

    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取请假记录成功",
        data=PaginatedResponse(
            items=processed_absents,
            total=total_count,
            page=page,
            page_size=page_size,
        )
    )

# 查看下属的所有请假请求
@router.get("/my_all_staffs_absents", response_model=BaseResponse[PaginatedResponse[AbsentCreateResponse]])
async def get_all_absents(
    page: int = 1,
    page_size: int = 10,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    sub_absents, total_count = await AbsentService.get_all_absent_by_responder_id(
        db_session=db_session,
        responder_id=current_user.id,
        page=page,
        page_size=page_size
    )

    # 转换为 Pydantic 模型
    processed_sub_absents = []
    for absent in sub_absents:
        processed_sub_absent = {
            "id": absent.id,
            "title": absent.title,
            "request_content": absent.request_content,
            "status": absent.status,
            "start_date": absent.start_date,
            "end_date": absent.end_date,
            "create_time": absent.create_time,
            "response_content": absent.response_content,
            "requester_id": absent.requester_id,
            "responder_id": absent.responder_id,
            "absent_type_id": absent.absent_type_id,
            "requester_name": absent.requester.username if absent.requester else "",
            "responder_name": absent.responder.username if absent.responder else None,
            "absent_type_name": absent.absent_type.name if absent.absent_type else ""
        }
        processed_sub_absents.append(processed_sub_absent)

    total_page = (total_count + page_size - 1) // page_size
    app_logger.info(f"获取下属请假记录成功，用户：{current_user.id}，总记录数：{total_count}，总页数：{total_page}")

    
    # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取下属请假记录成功",
        data=PaginatedResponse(
            items=processed_sub_absents,
            total=total_count,
            page=page,
            page_size=page_size,
        )
    )


# 查看还未处理的下属请假请求
@router.get("/my_unprocessed_staffs_absents", response_model=BaseResponse[PaginatedResponse[AbsentCreateResponse]])
async def get_all_absents(
    page: int = 1,
    page_size: int = 10,
    status: int = 1,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    sub_absents, total_count = await AbsentService.get_all_absent_by_responder_id_and_status(
        db_session=db_session,
        responder_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size
    )

    # 转换为 Pydantic 模型
    processed_sub_absents = []
    for absent in sub_absents:
        processed_sub_absent = {
            "id": absent.id,
            "title": absent.title,
            "request_content": absent.request_content,
            "status": absent.status,
            "start_date": absent.start_date,
            "end_date": absent.end_date,
            "create_time": absent.create_time,
            "response_content": absent.response_content,
            "requester_id": absent.requester_id,
            "responder_id": absent.responder_id,
            "absent_type_id": absent.absent_type_id,
            "requester_name": absent.requester.username if absent.requester else "",
            "responder_name": absent.responder.username if absent.responder else None,
            "absent_type_name": absent.absent_type.name if absent.absent_type else ""
        }
        processed_sub_absents.append(processed_sub_absent)

    total_page = (total_count + page_size - 1) // page_size
    app_logger.info(f"获取下属请假记录成功，用户：{current_user.id}，总记录数：{total_count}，总页数：{total_page}")

    
    # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取下属请假记录成功",
        data=PaginatedResponse(
            items=processed_sub_absents,
            total=total_count,
            page=page,
            page_size=page_size,
        )
    )

# 处理下属请假请求：必须status = 0；其它值则不可处理---即每个请假需求只处理一次
@router.patch("/my_staffs_absents/{absent_id}")
async def process_new_absents(
    absent_id: int,
    process_request: ProcessAbsentRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):    
    status = process_request.status
    response_content = process_request.response_content
    # 检查请假请求是否存在
    absent = await AbsentService.get_absent_by_id(db_session, absent_id)
    if not absent:
        raise BizException(ErrorCode.ABSENT_NOT_FOUND, 404)
    
    # 检查请假请求是否由当前用户处理
    if absent.responder_id != current_user.id:
        raise BizException(ErrorCode.NOT_PERMITTED, 403)
    
    # 检查请假请求状态是否为 1-待审批
    if absent.status != 1:
        raise BizException(ErrorCode.ABSENT_ALREADY_PROCESSED, 400)
    
    # 更新请假请求状态
    await AbsentService.update_absent_status(db_session, absent_id, status, response_content)
    
    app_logger.info(f"处理请假请求成功，请假ID：{absent_id}，用户：{current_user.id}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="处理请假请求成功",
        data=None
    )


# 获取审批人
@router.get("/responder", response_model=BaseResponse[AbsentResponder])
async def getresponder(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    try:
        responder =  await AbsentService.get_absent_responder(db_session, current_user)
    except BizException as e:
        app_logger.error(f"获取审批人失败，用户：{current_user.id}，错误：{e}")
        raise BizException(ErrorCode.SERVER_ERROR, 500)
    
    if not responder:
        raise BizException(ErrorCode.NOT_FOUND, 404)
    
    app_logger.info(f"获取审批人成功，用户：{current_user.id}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取审批人成功",
        data=AbsentResponder(
            email=responder.email,
            username=responder.username
        )
    )