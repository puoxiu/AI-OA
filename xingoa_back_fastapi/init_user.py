import asyncio
import shortuuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import OAUser, OADepartment, UserStatusChoices

from db.database import async_session
from utils.hash import get_password_hash


async def init_users():
    async with async_session() as db:
        try:
            # 获取部门
            department_names = ["董事会", "开发部", "运营部", "销售部", "人事部", "财务部"]
            result = await db.execute(select(OADepartment).where(OADepartment.name.in_(department_names)))
            departments = result.scalars().all()
            department_dict = {dept.name: dept for dept in departments}

            # 创建用户
            users = [
                {
                    "username": "xingxing",
                    "email": "xingxing@example.com",
                    "password": "123456",
                    "department": department_dict["董事会"],
                    "is_superuser": True,
                },
                {
                    "username": "mingzong",
                    "email": "mingzong@example.com",
                    "password": "123456",
                    "department": department_dict["董事会"],
                    "is_superuser": True,
                },
                {
                    "username": "zhangsan",
                    "email": "zhangsan@example.com",
                    "password": "123456",
                    "department": department_dict["开发部"],
                    "is_superuser": True,
                },
                {
                    "username": "lisi",
                    "email": "lisi@example.com",
                    "password": "123456",
                    "department": department_dict["运营部"],
                    "is_superuser": True,
                },
                {
                    "username": "wangwu",
                    "email": "wangwu@example.com",
                    "password": "123456",
                    "department": department_dict["销售部"],
                    "is_superuser": True,
                },
                {
                    "username": "zhaoliu",
                    "email": "zhaoliu@example.com",
                    "password": "123456",
                    "department": department_dict["人事部"],
                    "is_superuser": True,
                },
                {
                    "username": "qianqi",
                    "email": "qianqi@example.com",
                    "password": "123456",
                    "department": department_dict["财务部"],
                    "is_superuser": True,
                },
            ]

            for user_info in users:
                uid = shortuuid.uuid()
                hashed_password = get_password_hash(user_info["password"])
                new_user = OAUser(
                    uid=uid,
                    username=user_info["username"],
                    email=user_info["email"],
                    password_hashed=hashed_password,
                    is_superuser=user_info["is_superuser"],
                    status=UserStatusChoices.ACTIVED if user_info["is_superuser"] else UserStatusChoices.UNACTIVED,
                    department_id=user_info["department"].id  # 使用正确的 department_id 类型
                )
                db.add(new_user)
            await db.commit()

            # 重新获取用户
            usernames = ["xingxing", "mingzong", "zhangsan", "lisi", "wangwu", "zhaoliu", "qianqi"]
            result = await db.execute(select(OAUser).where(OAUser.username.in_(usernames)))
            users = result.scalars().all()
            user_dict = {user.username: user for user in users}

            # 给部门指定leader和manager
            department_dict["董事会"].leader = user_dict["xingxing"]
            department_dict["董事会"].manager = None

            department_dict["开发部"].leader = user_dict["zhangsan"]
            department_dict["开发部"].manager = user_dict["xingxing"]

            department_dict["运营部"].leader = user_dict["lisi"]
            department_dict["运营部"].manager = user_dict["xingxing"]

            department_dict["销售部"].leader = user_dict["wangwu"]
            department_dict["销售部"].manager = user_dict["xingxing"]

            department_dict["人事部"].leader = user_dict["zhaoliu"]
            department_dict["人事部"].manager = user_dict["mingzong"]

            department_dict["财务部"].leader = user_dict["qianqi"]
            department_dict["财务部"].manager = user_dict["mingzong"]

            await db.commit()
            print("用户初始化完成")
        except Exception as e:
            print(f"初始化用户时出错: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(init_users())