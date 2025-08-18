import asyncio
import shortuuid
from sqlalchemy import select
from app.models.inform import Inform, InformDepartment, InformRead
from app.models.meeting_room import MeetingRoom, MeetingBooking
from app.models.absent import AbsentType, Absent
from app.models.user import OADepartment,OAUser,UserStatusChoices,DepartmentRoleChoices,DepartmentUserRole
from utils.hash import get_password_hash
from db.database import Base, async_engine, async_session
# 建表
async def create_tables():
    async with async_engine.begin() as session:
        await session.run_sync(Base.metadata.create_all)


# 初始化数据
async def init_department():
    async with async_session() as session:
        try:
            result = await session.execute(select(OADepartment.name))
            existing_names = result.scalars().all()

            departments = [
                {"name": "董事会", "intro": "负责组织协调oa的各项工作"},
                {"name": "开发部", "intro": "负责产品开发"},
                {"name": "运营部", "intro": "负责运营"},
                {"name": "销售部", "intro": "负责o售"},
                {"name": "人事部", "intro": "负责人事"},
                {"name": "财务部", "intro": "负责财务"},
            ]
            for department in departments:
                if department["name"] not in existing_names:
                    new_department = OADepartment(name=department["name"], intro=department["intro"])
                    session.add(new_department)
                else:
                    print(f"部门 {department['name']} 已存在，跳过初始化")
            await session.commit()
            print("部门初始化完成")
        except Exception as e:
            print(f"初始化部门时出错: {e}")
            await session.rollback()

async def init_user():
    async with async_session() as session:
        try:
            # 1. 加载部门
            result = await session.execute(select(OADepartment))
            departments = result.scalars().all()
            department_dict = {dept.name: dept for dept in departments}
            
            # 2. 定义用户列表
            users_to_create = [
                {
                    "username": "星星",
                    "email": "xingxing@example.com",
                    "password": "123456",
                    "phone": "13800000000",
                    "department": department_dict["董事会"],
                    "is_superuser": True,
                    "role": DepartmentRoleChoices.LEADER,   # 董事会负责人
                },
                {
                    "username": "mingzong",
                    "email": "mingzong@example.com",
                    "password": "123456",
                    "phone": "13800000001",
                    "department": department_dict["董事会"],
                    "is_superuser": True,
                    "role": DepartmentRoleChoices.MEMBER,   # 董事会成员
                },
                {
                    "username": "zhangsan",
                    "email": "zhangsan@example.com",
                    "password": "123456",
                    "phone": "13800000002",
                    "department": department_dict["开发部"],
                    "is_superuser": True,
                    "role": DepartmentRoleChoices.LEADER,   # 开发部负责人
                },
                {
                    "username": "lisi",
                    "email": "lisi@example.com",
                    "password": "123456",
                    "phone": "13800000003",
                    "department": department_dict["运营部"],
                    "is_superuser": True,
                    "role": DepartmentRoleChoices.LEADER,   # 运营部负责人
                },
                {
                    "username": "wangwu",
                    "email": "wangwu@example.com",
                    "password": "123456",
                    "phone": "13800000004",
                    "department": department_dict["销售部"],
                    "is_superuser": True,
                    "role": DepartmentRoleChoices.LEADER,   # 销售部负责人
                },
                {
                    "username": "zhaoliu",
                    "email": "zhaoliu@example.com",
                    "password": "123456",
                    "phone": "13800000005",
                    "department": department_dict["人事部"],
                    "is_superuser": True,
                    "role": DepartmentRoleChoices.LEADER,   # 人事部负责人
                },
                {
                    "username": "qianqi",
                    "email": "qianqi@example.com",
                    "password": "123456",
                    "phone": "13800000006",
                    "department": department_dict["财务部"],
                    "is_superuser": True,
                    "role": DepartmentRoleChoices.LEADER,   # 财务部负责人
                },
            ]

            # 3. 检查用户是否已存在
            result = await session.execute(select(OAUser.username))
            existing_usernames = result.scalars().all()
                
            # 4. 创建用户
            for user_data in users_to_create:
                if user_data["username"] not in existing_usernames:
                    hashed_password = get_password_hash(user_data["password"])

                    user = OAUser(
                        id = shortuuid.uuid(),
                        username=user_data["username"],
                        email=user_data["email"],
                        password_hashed=hashed_password,
                        phone=user_data["phone"],
                        status=UserStatusChoices.ACTIVED,
                        is_superuser=user_data["is_superuser"],
                    )
                    session.add(user)
                    # 5. 关联部门角色
                    department_user_role = DepartmentUserRole(
                        user=user,
                        department=user_data["department"],
                        role=user_data["role"],
                    )
                    session.add(department_user_role)
                else:
                    print(f"用户 {user_data['username']} 已存在，跳过初始化")

            await session.commit()
            print("用户初始化完成")
        except Exception as e:
            print(f"初始化用户时出错: {e}")
            await session.rollback()

async def add_user_role():
    # 星星同时是：董事会、开发部、财务部的manager
    # mingzong同时是：运营部、销售部、人事部的manager
    async with async_session() as session:
        try:
            result = await session.execute(select(OADepartment))
            departments = result.scalars().all()
            department_dict = {dept.name: dept for dept in departments}
            extra_roles = {
                '星星': [
                    # (department_dict["董事会"], DepartmentRoleChoices.MANAGER),
                    (department_dict["开发部"], DepartmentRoleChoices.MANAGER),
                    (department_dict["财务部"], DepartmentRoleChoices.MANAGER),
                ],
                'mingzong': [
                    (department_dict["运营部"], DepartmentRoleChoices.MANAGER),
                    (department_dict["销售部"], DepartmentRoleChoices.MANAGER),
                    (department_dict["人事部"], DepartmentRoleChoices.MANAGER),
                ],
            }
            for username, roles in extra_roles.items():
                user_result = await session.execute(select(OAUser).where(OAUser.username == username))
                user = user_result.scalars().first()
                if user:
                    for department, role in roles:
                        # 检查用户在该部门是否已有角色
                        existing_role = await session.execute(
                            select(DepartmentUserRole).where(
                                DepartmentUserRole.user_id == user.id,
                                DepartmentUserRole.department_id == department.id
                            )
                        )
                        if existing_role.scalars().first():
                            print(f"用户 {username} 在 {department.name} 已有关联角色，跳过")
                            continue
                        department_user_role = DepartmentUserRole(
                            user=user,
                            department=department,
                            role=role,
                        )
                        session.add(department_user_role)
            await session.commit()
            print("用户角色添加完成")
        except Exception as e:
            print(f"添加用户角色时出错: {e}")
            await session.rollback()


async def init_absent():
    absent_types = [
        {"name": "事假"},
        {"name": "病假"},
        {"name": "年假"},
        {"name": "婚假"},
        {"name": "产假"},
        {"name": "陪产假"},
        {"name": "丧假"},
        {"name": "调休"},
        {"name": "工伤假"},
        {"name": "探亲假"},
    ]
    async with async_session() as session:
        try:
            # 1. 检查是否已存在
            result = await session.execute(select(AbsentType))
            existing_types = result.scalars().all()
            if existing_types:
                print("请假类型已存在，无需重复初始化")
                return
            # 2. 创建请假类型
            for type_data in absent_types:
                new_type = AbsentType(
                    name=type_data["name"],
                )
                session.add(new_type)
            await session.commit()
            print("请假类型初始化完成")
        except Exception as e:
            print(f"初始化请假类型时出错: {e}")
            await session.rollback()

async def init_MeetingRoom():
    meeting_rooms = [
        {"room_number": "804", "description": "804会议室，常用于小组例会", "equipment": "投影仪,白板,麦克风", "capacity": 15},
        {"room_number": "904", "description": "904会议室，常用于小组例会", "equipment": "投影仪,白板,麦克风", "capacity": 15},
        {"room_number": "806", "description": "806会议室，常用于项目会议", "equipment": "投影仪,白板,麦克风,摄像头", "capacity": 20},
        {"room_number": "906", "description": "906会议室，常用于项目会议", "equipment": "投影仪,白板,麦克风,摄像头", "capacity": 20},
        {"room_number": "910", "description": "910会议室，常用于部门会议", "equipment": "投影仪,白板,麦克风,摄像头,矿泉水", "capacity": 100},
        {"room_number": "1001", "description": "1001会议室，常用于公司会议", "equipment": "投影仪,白板,麦克风,摄像头,矿泉水,座位平板", "capacity": 500},
    ]

    async with async_session() as session:
        try:
            # 1. 检查是否已存在
            result = await session.execute(select(MeetingRoom))
            existing_rooms = result.scalars().all()
            if existing_rooms:
                print("会议房间已存在，无需重复初始化")
                return
            # 2. 创建会议房间
            for room_data in meeting_rooms:
                new_room = MeetingRoom(
                    room_number=room_data["room_number"],
                    description=room_data["description"],
                    equipment=room_data["equipment"],
                    capacity=room_data["capacity"],
                )
                session.add(new_room)
            await session.commit()
            print("会议房间初始化完成")
        except Exception as e:
            print(f"初始化会议房间时出错: {e}")
            await session.rollback()

async def init_data():
    await init_department()
    await init_user()
    await add_user_role()
    await init_absent()
    await init_MeetingRoom()


async def main():
    await create_tables()
    await init_data()


if __name__ == "__main__":
    asyncio.run(main())