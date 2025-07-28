from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.department import DepartmentResponse
from app.services.department import DepartmentService
from deps.deps import get_db_session


router = APIRouter(
    prefix="/api/v1/department",
    tags=["部门信息"]
)


# 获取所有部门信息
@router.get("/all", response_model=List[DepartmentResponse])
async def get_all_departments(db_session: AsyncSession = Depends(get_db_session)):
    departments = await DepartmentService.get_all_departments(db_session)
    return departments

