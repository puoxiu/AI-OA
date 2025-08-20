from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.home import (
    LatestInformResponse,
    LatestAbsentResponse,
    DepartmentStaffCountResponse
)
from app.services.home import HomeService
from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser
from app.response_model import BaseResponse
from app.error import ErrorCode

router = APIRouter(
    prefix="/api/v1/home",
    tags=["首页数据"]
)


# 最新通知
@router.get("/latest/inform", response_model=BaseResponse[List[LatestInformResponse]])
async def get_latest_inform(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    data = await HomeService.get_latest_informs(db_session, current_user)
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取最新通知成功",
        data=data
    )

# 最新考勤
@router.get("/latest/absent", response_model=BaseResponse[List[LatestAbsentResponse]])
async def get_latest_absent(
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user)
):
    data = await HomeService.get_latest_absents(db_session, current_user)
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取最新考勤成功",
        data=data
    )

# 部门员工数量统计
@router.get("/department/staff/count", response_model=BaseResponse[List[DepartmentStaffCountResponse]])
async def get_department_staff_count(
    db_session: AsyncSession = Depends(get_db_session)
):
    data = await HomeService.get_department_staff_count(db_session)
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取部门员工统计成功",
        data=data
    )

# 健康检查
@router.get("/health", response_model=BaseResponse)
async def health_check():
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="服务正常"
    )