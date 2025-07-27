import os
from celery import Celery

print("test!!!!!")
# 设置FastAPI的环境变量

# 创建Celery实例
celery_app = Celery(
    "xingoa_fastapi",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/1",
)
import utils.celery_tasks
# 自动发现任务
celery_app.autodiscover_tasks(['utils'])
