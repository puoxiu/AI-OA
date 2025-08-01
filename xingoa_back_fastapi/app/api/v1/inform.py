from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.inform import InformsResponse, InformCreateRequest
from app.services.inform import InformService
from deps.deps import get_db_session, get_current_user

from app.models.inform import Inform
from app.models.user import OAUser

from app.response_model import BaseResponse
from app.error import ErrorCode

router = APIRouter(
    prefix="/api/v1/inform",
    tags=["通知管理"]
)

# 查询所有可见的通知
@router.get("/all", response_model=BaseResponse[List[InformsResponse]])
async def get_informs(db_session: AsyncSession = Depends(get_db_session), current_user: OAUser = Depends(get_current_user)):
    informs = await InformService.get_informs(db_session, current_user)
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取通知信息成功",
        data=informs
    )


# 创建新的通知
@router.post("/create")
async def create_inform(
    inform: InformCreateRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    print("=" * 300)
    inform = await InformService.create_inform(db_session, inform.title, inform.content, inform.public, current_user)

    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="创建通知成功",
        data=inform
    )

# 通知已读功能
@router.post("/{inform_id}/read")
async def mark_inform_as_read(
    inform_id: int,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    result = await InformService.mark_inform_as_read(db_session, inform_id, current_user)
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="标记通知为已读成功",
        data=result
    )
