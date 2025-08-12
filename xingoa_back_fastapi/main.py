from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncEngine
from contextlib import asynccontextmanager
from sqlalchemy import text
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from db.database import async_engine, Base
from app.api.v1 import auth, absent, inform, staff, department, meeting_room, meeting_booking
from app.exceptions import BizException
from app.error import ErrorCode
from app.core.logging import app_logger

# 生命周期管理器
# 仅在开发环境推荐使用
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时
    async with async_engine.begin() as conn:
        # 遍历所有继承自 Base 的 ORM 模型类，根据模型定义在数据库中创建对应的表结构
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("SELECT 1"))
            app_logger.info("数据库连接成功")
        except Exception as e:
            app_logger.error(f"数据库连接失败: {e}")
            # 可选：在连接失败时阻止应用启动
            raise
    
    yield  # 应用运行时
    
    # 应用关闭时
    if isinstance(async_engine, AsyncEngine):
        await async_engine.dispose()
        app_logger.info("数据库连接池已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许哪些源访问，* 表示所有（不推荐生产用）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 自定义异常处理器
@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    app_logger.warning(f"业务异常: {exc.detail['msg']}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.detail["code"],
            "msg": exc.detail["msg"]
        }
    )
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_logger.error(f"未处理异常, 系统错误: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": ErrorCode.SERVER_ERROR,
            "msg": "服务器内部错误，请联系管理员！"
        }
    )
# 处理请求验证失败（如参数格式错误）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    app_logger.warning(f"请求参数校验失败: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "msg": "请求参数校验失败，请检查请求内容和格式！"
        }
    )
# 未登录 未传入token -》 401 未授权异常


# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(absent.router)
app.include_router(inform.router)
app.include_router(staff.router)
app.include_router(department.router)
app.include_router(meeting_room.router)
app.include_router(meeting_booking.router)

# 测试邮箱发送路由
@app.get("/test-email")
async def test_email():
    from utils.mailer import send_email
    try:
        send_email("测试邮件", ["zmx_12345@163.com"], "这是一封测试邮件")
        app_logger.debug("测试邮件发送成功")
        return {"message": "测试邮件发送成功"}
    except Exception as e:
        app_logger.error(f"测试邮件发送失败: {e}")
        return {"message": f"测试邮件发送失败: {e}"}



if __name__ == "__main__":
    import uvicorn
    app_logger.info("应用启动")
    uvicorn.run(app, host="0.0.0.0", port=8003)