from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.services.staff import StaffService
from app.schemas.staff import AddStaffRequest
from deps.deps import get_db_session, get_current_user
from app.models.user import User


router = APIRouter(
    "/api/v1/staff",
    tags=["员工管理"],
)


# 添加新员工
# @router.post("/add")
# async def add_staff(
#     staff: AddStaffRequest,
#     db_session: AsyncSession = Depends(get_db_session),
#     current_user: User = Depends(get_current_user),
# ):
    # 必须是人事部的hr才能添加新员工