from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import shortuuid
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.models.user import OAUser, UserStatusChoices, DepartmentUserRole, DepartmentRoleChoices
from app.core.config import settings
from utils.hash import get_password_hash
from utils.aeser import AESCipher
# from utils.mailer import send_email
from utils.celery_tasks import send_email_task
from app.schemas.paginate import PaginatedResponse
from app.schemas.staff import StaffResponse, DepartmentBriefResponse

aes = AESCipher(settings.SECRET_KEY)

class StaffService:
    @staticmethod
    async def create_staff(db_session: AsyncSession, username: str, email: str, password: str, department_id: int, phone: str) -> OAUser:
        password_hashed = get_password_hash(password)
        id = shortuuid.uuid()

        new_staff = OAUser(
            id=id,
            username=username,
            email=email,
            password_hashed=password_hashed,
            phone=phone,
            status=UserStatusChoices.UNACTIVED,
        )
        db_session.add(new_staff)

        if department_id:
            # 创建中间表记录，建立用户与部门的关联
            dept_user_role = DepartmentUserRole(
                user_id=id,  # 关联当前创建的用户
                department_id=department_id,  # 目标部门ID
                role=DepartmentRoleChoices.MEMBER  # 默认角色为部门成员
            )
            db_session.add(dept_user_role)

        await db_session.commit()
        
        # 发送激活邮件
        # 这个 token 是对 email 使用 AES 加密后的结果。        
        token = aes.encrypt(email)
        # print(f"生成的token={token}")
        # 激活链接
        # active_url = f"{settings.BASE_URL}/staff/activate?token={token}"
        active_url = f"{settings.BASE_URL}/static/activate_result.html?token={token}"

        message = f"""
        你好，{username}：
        感谢您注册xx公司oa系统。为了确保您的账户安全以及账户的正常使用，请点击以下链接激活您的账户：
        {active_url}
        如果您没有在oa系统注册过，或者不希望激活账户，请忽略此邮件。
        请注意：此链接有效期为24小时。
        感谢您的参与！
        oa系统团队
        
        此邮件由系统自动发送，请勿直接回复。
        """

        # 发送邮件
        send_email_task.delay(subject="oa系统账户激活", recipient_list=[email], message=message)

        return new_staff
    
    @staticmethod
    def decrypt_token(token: str) -> str:
        # 返回解密的email
        return aes.decrypt(token)
    

    @staticmethod
    async def activate_staff(user: OAUser, db_session: AsyncSession):
        user.status = UserStatusChoices.ACTIVED
        db_session.add(user)
        await db_session.commit()


    @staticmethod
    async def get_staff_list(db_session: AsyncSession, page: int = 1, page_size: int = 10, department_id: int = None, sort_order: str = "desc") -> PaginatedResponse[StaffResponse]:
        """
        获取员工列表（支持分页、部门筛选、排序）
        :param department_id: 部门ID，为None时不筛选
        :param sort_order: 排序方向（"desc"降序/"asc"升序），默认按加入时间排序
        """
        # 1. 处理分页参数（确保page和page_size有效）
        page = max(page, 1)
        offset = (page - 1) * page_size

        # 2. 构建基础查询（预加载关联的部门角色和部门信息）
        query = select(OAUser).options(
            selectinload(OAUser.department_roles).selectinload(DepartmentUserRole.department)
        )

        # 3. 部门筛选（如果department_id存在）
        if department_id is not None:
            query = query.where(
                # 筛选出所属部门包含department_id的用户
                OAUser.department_roles.any(DepartmentUserRole.department_id == department_id)
            )

        # 4. 排序（默认按加入时间date_joined排序）
        if sort_order.lower() == "desc":
            query = query.order_by(OAUser.date_joined.desc())  # 降序（最新加入在前）
        else:
            query = query.order_by(OAUser.date_joined.asc())  # 升序（最早加入在前）

        # 5. 分页查询：获取当前页数据
        paginated_query = query.offset(offset).limit(page_size)
        result = await db_session.execute(paginated_query)
        staff_list = result.scalars().all()

        # 6. 查询总记录数（用于计算总页数）总记录数需应用相同的部门筛选条件
        total_query = select(func.count()).select_from(OAUser)
        if department_id is not None:
            total_query = total_query.where(
                OAUser.department_roles.any(DepartmentUserRole.department_id == department_id)
            )
        total_result = await db_session.execute(total_query)
        total = total_result.scalar_one()  # 总记录数

        # 7. 计算总页数
        total_page = (total + page_size - 1) // page_size  # 向上取整

        # 8. 转换为StaffResponse列表（处理部门信息）
        staff_responses = []
        for staff in staff_list:
            # 提取用户所属的部门信息（去重，避免重复部门）
            departments = [
                DepartmentBriefResponse(
                    id=role.department.id,
                    name=role.department.name
                )
                for role in staff.department_roles
                if role.department  # 确保部门信息已加载
            ]
            # 去重（如果用户在同一部门有多个角色）
            unique_departments = []
            seen_dept_ids = set()
            for dept in departments:
                if dept.id not in seen_dept_ids:
                    seen_dept_ids.add(dept.id)
                    unique_departments.append(dept)

            # 构造StaffResponse
            staff_responses.append(StaffResponse(
                id=staff.id,
                username=staff.username,
                email=staff.email,
                phone=staff.phone,
                status=staff.status,
                date_joined=staff.date_joined,
                departments=unique_departments,
                is_superuser=staff.is_superuser
            ))

        # 9. 返回分页响应对象
        return PaginatedResponse(
            items=staff_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_page=total_page
        )
