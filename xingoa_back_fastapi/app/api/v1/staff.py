from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.services.staff import StaffService
from app.services.auth import UserService
from app.schemas.staff import AddStaffRequest
from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser, UserStatusChoices


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

    # 验证用户名是否已存在
    if await UserService.get_user_by_username(db_session, staffReq.realname):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已存在",
        )

    # 验证当前用户是否是人事部的hr
    if current_user.department.name != "人事部":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有人事部的hr才能添加新员工",
        )

    # 创建新员工, 会向新员工的邮箱发送激活邮件，此时员工状态为未激活；待新员工点击激活链接后，员工状态会改为已激活
    new_staff = await StaffService.create_staff(db_session, staffReq.realname, staffReq.email, staffReq.password, staffReq.department_id, staffReq.phone)
    return JSONResponse(content={"message": "添加新员工邮件发送成功", "uid": new_staff.uid}, status_code=status.HTTP_201_CREATED)


# 用户点击激活链接，激活账户
@router.get("/activate")
async def activate_user(
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
):
    # 从请求参数重获取 邮箱加密生成的token
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活链接参数错误",
        )
    
    # 解密token
    try:
        # print(f"token = {token}")
        email = StaffService.decrypt_token(token=token)
    except Exception as e:
        # 解密失败（如token被篡改）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活链接无效：token格式错误"
        )
    
    # 根据邮箱查询用户
    user = await UserService.get_user_by_email(db_session, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该用户"
        )

    # 验证用户状态
    if user.status == UserStatusChoices.ACTIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该账号已激活，无需重复操作"
        )
    if user.status != UserStatusChoices.UNACTIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号状态异常，无法激活"
        )

    # todo 添加token有效期机制--基于redis


    # 激活用户
    try:
        await StaffService.activate_staff(user, db_session)
        return {"status": "success", "message": "账号激活成功！"} 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="激活失败!"
        )
    





