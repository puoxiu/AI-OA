from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.inform import InformsResponse, InformCreateRequest
from app.services.inform import InformService
from deps.deps import get_db_session
from app.core.common import get_current_user
from app.models.inform import Inform
from app.models.user import OAUser


router = APIRouter(
    prefix="/api/v1/inform",
    tags=["通知管理"]
)

# 查询所有可见的通知
@router.get("/all", response_model=List[InformsResponse])
async def get_informs(db_session: AsyncSession = Depends(get_db_session), current_user: OAUser = Depends(get_current_user)):
    informs = await InformService.get_informs(db_session, current_user)
    return informs


# 创建新的通知
@router.post("")
async def create_inform(
    inform: InformCreateRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    inform = await InformService.create_inform(db_session, inform.title, inform.content, inform.public, current_user)

    return inform

# 通知已读功能
@router.post("/{inform_id}/read")
async def mark_inform_as_read(
    inform_id: int,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    result = await InformService.mark_inform_as_read(db_session, inform_id, current_user)
    return result
