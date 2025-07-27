from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import shortuuid

from app.models.user import OAUser, UserStatusChoices
from app.core.config import settings
from utils.hash import get_password_hash
from utils.aeser import AESCipher
# from utils.mailer import send_email
from utils.celery_tasks import send_email_task

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
        # 激活链接
        active_url = f"{settings.BASE_URL}/staff/activate?token={token}"
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