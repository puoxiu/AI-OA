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

router = APIRouter(
    prefix="/api/v1/absent",
    tags=["考勤管理"]
)

from typing import List

@router.get("/type", response_model=List[AbsentTypeResponse])
async def get_absent_type(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """
    获取请假类型
    """
    absent_types = await AbsentTypeService.get_all_absent_type(db_session)

    return absent_types


@router.post("/")
async def create_new_absent(
    absent: AbsentCreateRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    """
    发出请假
    """
    responder = get_responder(current_user)
    if responder is None:
        raise HTTPException(status_code=500, detail="这里错误")

    new_absent = await AbsentService.create_absent(db_session, absent, current_user.uid, responder.uid)
    return Response(
        content="请假成功!"
    )

# 查看自己的所有请求
@router.get("/my_absents", response_model=list[AbsentCreateResponse])
async def get_all_absents(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    try:
        my_absents = await AbsentService.get_all_absent_by_requester_uid(
            db_session=db_session,
            requester_uid=current_user.uid
        )
        
        # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
        return my_absents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取请假记录失败：{str(e)}"
        )

# 查看下属的所有请假请求
@router.get("/my_all_staffs_absents", response_model=list[AbsentCreateResponse])
async def get_all_absents(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    try:
        my_absents = await AbsentService.get_all_absent_by_responder_uid(
            db_session=db_session,
            responder_uid=current_user.uid
        )
        # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
        return my_absents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取请假记录失败：{str(e)}"
        )

# 查看还未处理的下属请假请求
@router.get("/my_staffs_absents", response_model=list[AbsentCreateResponse])
async def get_all_absents(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    try:
        my_absents = await AbsentService.get_all_absent_by_responder_uid_and_status(
            db_session=db_session,
            responder_uid=current_user.uid
        )
        
        # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
        return my_absents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取请假记录失败：{str(e)}"
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
        raise HTTPException(status_code=404, detail="请假请求不存在")
    
    # 检查请假请求是否由当前用户处理
    if absent.responder_uid != current_user.uid:
        raise HTTPException(status_code=403, detail="您没有权限处理该请假请求")
    
    # 检查请假请求状态是否为0
    if absent.status != 0:
        raise HTTPException(status_code=400, detail="该请假请求已处理")
    
    # 更新请假请求状态
    try:
        await AbsentService.update_absent_status(db_session, absent_id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新请假请求状态失败：{str(e)}")

