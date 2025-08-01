from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.department import DepartmentResponse
from app.services.department import DepartmentService
from deps.deps import get_db_session
from app.response_model import BaseResponse
from app.error import ErrorCode
from app.core.logging import app_logger

router = APIRouter(
    prefix="/api/v1/department",
    tags=["部门信息"]
)


# 获取所有部门信息
@router.get("/all", response_model=BaseResponse[List[DepartmentResponse]])
async def get_all_departments(db_session: AsyncSession = Depends(get_db_session)):
    departments = await DepartmentService.get_all_departments(db_session)
    
    app_logger.info(f"获取部门信息成功，部门数量：{len(departments)}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        msg="获取部门信息成功",
        data=departments
    )

