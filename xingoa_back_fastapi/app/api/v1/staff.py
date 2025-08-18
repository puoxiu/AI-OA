from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.services.staff import StaffService
from app.services.auth import UserService
from app.schemas.staff import AddStaffRequest
from deps.deps import get_db_session, get_current_user
from app.models.user import OAUser, UserStatusChoices
from app.schemas.paginate import PaginatedResponse
from app.schemas.staff import StaffResponse
from app.exceptions import BizException
from app.error import ErrorCode
from app.response_model import BaseResponse
from app.core.logging import app_logger

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
    # 必须是人事部的hr 或者is_superuser 才能添加新员工
    if not current_user.is_superuser:
        user_departments = {
            role.department.name 
            for role in current_user.department_roles if role.department
        }
        if "人事部" not in user_departments:
            app_logger.error(f"用户 {current_user.id} 没有权限获取员工列表")
            raise BizException(ErrorCode.NOT_PERMITTED, 403)
    
    # 验证邮箱是否已存在
    if await UserService.get_user_by_email(db_session, staffReq.email):
        raise BizException(ErrorCode.USER_OR_EMAIL_EXIST, 400)

    # 验证用户名是否已存在
    if await UserService.get_user_by_username(db_session, staffReq.realname):
        raise BizException(ErrorCode.USER_OR_EMAIL_EXIST, 400)
    

    # 创建新员工, 会向新员工的邮箱发送激活邮件，此时员工状态为未激活；待新员工点击激活链接后，员工状态会改为已激活
    new_staff = await StaffService.create_staff(db_session, staffReq.realname, staffReq.email, staffReq.password, staffReq.department_id, staffReq.phone)
    # return JSONResponse(content={"message": "添加新员工邮件发送成功", "id": new_staff.id}, status_code=status.HTTP_201_CREATED)
    
    app_logger.info(f"添加新员工发送邮件成功，员工ID：{new_staff.id}，邮箱：{staffReq.email}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        message="添加新员工邮件发送成功",
        data={
            "id": new_staff.id,
            "email": new_staff.email,
            "password": staffReq.password,
        },
    )


# 用户点击激活链接，激活账户
@router.get("/activate")
async def activate_user(
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
):
    # 从请求参数重获取 邮箱加密生成的token
    token = request.query_params.get("token")
    if not token:
        raise BizException(ErrorCode.NOT_PERMITTED, 400)
    
    # 解密token--err属于server error
    email = StaffService.decrypt_token(token=token)
    
    # 根据邮箱查询用户
    user = await UserService.get_user_by_email(db_session, email)
    if not user:
        raise BizException(ErrorCode.EMAIL_OR_USERNAME_NOT_FOUND, 400)

    # 验证用户状态
    if user.status == UserStatusChoices.ACTIVED:
        raise BizException(ErrorCode.REPEAT_OPERATION, 400)
    if user.status != UserStatusChoices.UNACTIVED:
        raise BizException(ErrorCode.STATUS_EXCEPTION, 400)

    # todo 添加token有效期机制--基于redis


    # 激活用户-失败也是server error全局异常捕获
    await StaffService.activate_staff(user, db_session)
    
    app_logger.info(f"员工账号激活成功，员工ID：{user.id}，邮箱：{user.email}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        message="账号激活成功！",
    )

    

# 员工列表， 支持分页 + 筛选
# 必须是人事部的hr或者superuser才能获取员工列表
@router.get("/list", response_model=BaseResponse[PaginatedResponse[StaffResponse]])
async def get_staff_list(
    page: int = 1,
    page_size: int = 10,
    department_id: int = None,
    db_session: AsyncSession = Depends(get_db_session),
    current_user: OAUser = Depends(get_current_user),
):
    if not current_user.is_superuser:
        user_departments = {
            role.department.name 
            for role in current_user.department_roles if role.department
        }
        if "人事部" not in user_departments:
            app_logger.error(f"用户 {current_user.id} 没有权限获取员工列表")
            raise BizException(ErrorCode.NOT_PERMITTED, 403)
    
    # 获取员工列表， 可以分页 + 筛选 + 排序
    staff_list = await StaffService.get_staff_list(db_session, page, page_size, department_id, "desc")
    
    app_logger.info(f"获取员工列表成功，用户：{current_user.id}，部门ID：{department_id}，页码：{page}，每页数量：{page_size}")
    
    return BaseResponse(
        code=ErrorCode.SUCCESS,
        message="获取员工列表成功",
        data=staff_list,
    )



