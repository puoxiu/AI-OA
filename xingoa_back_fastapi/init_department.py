import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import async_session
from app.models.user import OADepartment

async def init_departments():
    async with async_session() as db:
        try:
            departments = [
                {"name": "董事会", "intro": "负责组织协调oa的各项工作"},
                {"name": "开发部", "intro": "负责产品开发"},
                {"name": "运营部", "intro": "负责运营"},
                {"name": "销售部", "intro": "负责o售"},
                {"name": "人事部", "intro": "负责人事"},
                {"name": "财务部", "intro": "负责财务"},
            ]
            for department in departments:
                new_department = OADepartment(name=department["name"], intro=department["intro"])
                db.add(new_department)
            await db.commit()
            print("部门初始化完成")
        except Exception as e:
            print(f"初始化部门时出错: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(init_departments())