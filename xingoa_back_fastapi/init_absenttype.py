import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import async_session
from app.models.absent import AbsentType
from sqlalchemy import select, func

async def init_absent_types():
    async with async_session() as db:
        try:
            # 检查是否已有数据
            count = await db.scalar(select(func.count(AbsentType.id)))
            if count > 0:
                print("请假类型已存在，无需重复初始化")
                return

            # 定义请假类型数据（移除intro字段，因为模型中没有）
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

            # 创建并添加到数据库
            for type_data in absent_types:
                new_type = AbsentType(**type_data)  # 使用解包方式创建对象
                db.add(new_type)

            await db.commit()
            print("请假类型初始化完成")

        except Exception as e:
            print(f"初始化请假类型时出错: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(init_absent_types())