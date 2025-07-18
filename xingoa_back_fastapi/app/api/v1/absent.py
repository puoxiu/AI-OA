# AI-OA/xingoa_back_fastapi/app/api/v1/absent.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.absent import AbsentCreateResponse, AbsentCreateRequest, AbsentTypeResponse
from app.services.absent import AbsentService, AbsentTypeService
from deps.deps import get_db_session
from app.core.auth import AuthTokenHelper
from app.models.user import OAUser
from app.services.auth import UserService
from app.utils.absent import get_responder

router = APIRouter(
    prefix="/api/v1/absent",
    tags=["考勤管理"]
)

# 获取类型
from typing import List
@router.get("/type", response_model=List[AbsentTypeResponse])
async def get_absent_type(
    db_session: AsyncSession = Depends(get_db_session),
    token: str = Depends(AuthTokenHelper.get_token)
):
    """
    获取请假类型
    """
    payload = AuthTokenHelper.token_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="请先登录！")

    absent_types = await AbsentTypeService.get_all_absent_type(db_session)
    # 将ORM对象转换为Pydantic模型列表
    # return [AbsentTypeResponse.model_validate(type) for type in absent_types]
    return absent_types


@router.post("/")
async def create_new_absent(
    absent: AbsentCreateRequest,
    db_session: AsyncSession = Depends(get_db_session),
    token: str = Depends(AuthTokenHelper.get_token)
):
    """
    发出请假
    """
    payload = AuthTokenHelper.token_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="请先登录！")
    
    email = payload.get("email")
    user = await UserService.get_user_by_email(db_session, email)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    # 这里需要实现获取审批者的逻辑

    responder = get_responder(user)
    if responder is None:
        raise HTTPException(status_code=500, detail="这里错误")

    new_absent = await AbsentService.create_absent(db_session, absent, user.uid, responder.uid)
    return Response(
        content="请假成功!"
    )

# 查看自己的所有请求
@router.get("/my_absents", response_model=list[AbsentCreateResponse])
async def get_all_absents(
    db_session: AsyncSession = Depends(get_db_session),
    token: str = Depends(AuthTokenHelper.get_token)
):
    payload = AuthTokenHelper.token_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="请先登录！")
    
    email = payload.get("email")
    user = await UserService.get_user_by_email(db_session, email)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    try:
        my_absents = await AbsentService.get_all_absent_by_requester_uid(
            db_session=db_session,
            requester_uid=user.uid
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
    token: str = Depends(AuthTokenHelper.get_token)
):
    payload = AuthTokenHelper.token_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="请先登录！")
    
    email = payload.get("email")
    user = await UserService.get_user_by_email(db_session, email)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    try:
        my_absents = await AbsentService.get_all_absent_by_responder_uid(
            db_session=db_session,
            responder_uid=user.uid
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
    token: str = Depends(AuthTokenHelper.get_token)
):
    payload = AuthTokenHelper.token_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="请先登录！")
    
    email = payload.get("email")
    user = await UserService.get_user_by_email(db_session, email)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    try:
        my_absents = await AbsentService.get_all_absent_by_responder_uid_and_status(
            db_session=db_session,
            responder_uid=user.uid
        )
        
        # 直接返回 ORM 实例列表，FastAPI 会自动通过 response_model 验证并转换
        return my_absents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取请假记录失败：{str(e)}"
        )

# 处理下属请假请求：必须status = 0；其它值则不可处理---即每个请假需求只处理一次

