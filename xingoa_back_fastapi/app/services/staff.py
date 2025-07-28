from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import shortuuid
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.models.user import OAUser, UserStatusChoices
from app.core.config import settings
from utils.hash import get_password_hash
from utils.aeser import AESCipher
# from utils.mailer import send_email
from utils.celery_tasks import send_email_task
from app.schemas.paginate import PaginatedResponse
from app.schemas.staff import StaffResponse

aes = AESCipher(settings.SECRET_KEY)

class StaffService:
    @staticmethod
    async def create_staff(db_session: AsyncSession, username: str, email: str, password: str, department_id: int, phone: str = None) -> OAUser:
        password_hashed = get_password_hash(password)
        uid = shortuuid.uuid()
        new_staff = OAUser(
            uid=uid,
            username=username,
            email=email,
            password_hashed=password_hashed,
            phone=phone,
            department_id=department_id,
            status=UserStatusChoices.UNACTIVED,
        )
        db_session.add(new_staff)
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
    async def get_staff_list(db_session: AsyncSession, page: int = 1, page_size: int = 10, department_id: int = None,
    sort_field: str = "id", sort_order: str = "desc"):
        try:
            # 基础查询
            query = select(OAUser).options(
                joinedload(OAUser.department)
            )
            
            # 筛选条件
            if department_id:
                query = query.filter(OAUser.department_id == department_id)
            
            # 计算总记录数（单独查询，不包含分页逻辑）
            count_query = select(func.count(OAUser.uid))
            if department_id:
                count_query = count_query.filter(OAUser.department_id == department_id)
            
            total_result = await db_session.execute(count_query)
            total = total_result.scalar() or 0
            
            # 处理排序
            if hasattr(OAUser, sort_field):
                sort_expr = getattr(OAUser, sort_field)
                if sort_order.lower() == "desc":
                    sort_expr = sort_expr.desc()
                query = query.order_by(sort_expr)
            
            # 分页
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            # 执行查询
            result = await db_session.execute(query)
            staff_list = result.scalars().all()
            
            # 将 ORM 对象列表转换为 Pydantic 模型列表
            staff_list = [StaffResponse.from_orm(staff) for staff in staff_list]

            return PaginatedResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=staff_list
            )
        except Exception as e:
            await db_session.rollback()
            raise e
