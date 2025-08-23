import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from ai.ai_config import ai_settings

def setup_ai_chat_logging():
    # 创建日志目录
    log_dir = Path(ai_settings.AI_LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / ai_settings.AI_LOG_FILE

    # 日志格式（包含时间、模块、级别、消息）
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 初始化日志器
    logger = logging.getLogger("app")
    logger.setLevel(ai_settings.AI_LOG_LEVEL.value)  # 从配置获取级别
    logger.handlers.clear()  # 避免重复添加处理器

    # 1. 文件日志处理器（始终启用）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=ai_settings.AI_LOG_MAX_BYTES,
        backupCount=ai_settings.AI_LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. 控制台日志处理器（根据配置决定是否启用）
    if ai_settings.AI_LOG_CONSOLE_OUTPUT:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 屏蔽第三方库的冗余日志（如uvicorn、sqlalchemy）
    for lib in ["uvicorn", "sqlalchemy", "fastapi"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return logger

# 全局日志实例
ai_logger = setup_ai_chat_logging()
