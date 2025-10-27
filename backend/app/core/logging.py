"""
日志配置
"""

import sys
import logging
from loguru import logger
from app.core.config import settings


def setup_logging():
    """设置应用日志配置"""

    # 移除默认的loguru处理器
    logger.remove()

    # 控制台输出格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # 文件输出格式（JSON格式，便于分析）
    if not settings.DEBUG:
        logger.add(
            "logs/app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=False,
            diagnose=False
        )

        # 错误日志单独记录
        logger.add(
            "logs/error.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

    # 重定向标准库logging到loguru
    logging.basicConfig(handlers=[logging.NullHandler()], level=0, force=True)

    class InterceptHandler(logging.Handler):
        """拦截标准库logging并转发到loguru"""

        def emit(self, record):
            try:
                # Get corresponding Loguru level if it exists
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # 配置标准库logging使用loguru
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_LEVEL)

    # 禁用一些过于详细的日志
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]
    logging.getLogger("sqlalchemy.engine").handlers = [InterceptHandler()]

    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger