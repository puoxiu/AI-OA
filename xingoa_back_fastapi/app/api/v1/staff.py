from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.services.staff import StaffService
from app.services.auth import UserService
from app.schemas.staff import AddStaffRequest
from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser


router = APIRouter(
    prefix="/api/v1/staff",
    tags=["员工管理"],
)


# 添加新员工
@router.post("/add")
async def add_staff(
    staffReq: AddStaffRequest,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user),
):
    # 必须是人事部的hr才能添加新员工
    
    # 验证邮箱是否已存在
    if await UserService.get_user_by_email(db_session, staffReq.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已存在",
        )

    # 验证当前用户是否是人事部的hr
    if current_user.department.name != "人事部":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有人事部的hr才能添加新员工",
        )

    # 创建新员工, 会向新员工的邮箱发送激活邮件，此时员工状态为未激活；待新员工点击激活链接后，员工状态会改为已激活
    new_staff = await StaffService.create_staff(db_session, staffReq.realname, staffReq.email, staffReq.password, staffReq.department_id, staffReq.phone)
    return JSONResponse(content={"message": "员工添加成功", "uid": new_staff.uid}, status_code=status.HTTP_201_CREATED)


# 用户点击激活链接，激活账户
@router.get("/activate")
async def activate_user(
    db_session: AsyncSession = Depends(get_db_session),
):
    # 从请求参数中获取uid
    return JSONResponse(content={"message": "激活成功"}, status_code=status.HTTP_200_OK)
# 用户点击  