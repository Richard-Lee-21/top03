#!/usr/bin/env python3
"""
Top3-Hunter Backend Server
动态商品推荐引擎后端服务
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.exceptions import AppException

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 Top3-Hunter Backend 正在启动...")

    # 这里可以添加启动时的初始化逻辑
    # 例如：数据库连接检查、Redis连接检查等

    logger.info("✅ Top3-Hunter Backend 启动完成")

    yield

    # 关闭时执行
    logger.info("🛑 Top3-Hunter Backend 正在关闭...")


# 创建FastAPI应用实例
app = FastAPI(
    title="Top3-Hunter API",
    description="动态商品推荐引擎后端API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 受信任主机中间件
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# 全局异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理应用自定义异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误" if not settings.DEBUG else str(exc),
            "code": "INTERNAL_SERVER_ERROR"
        }
    )


# 健康检查端点
@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "success",
        "message": "Top3-Hunter Backend is running",
        "version": "1.0.0",
        "timestamp": time.time()
    }


# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# 为了向后兼容，重定向旧API路径
@app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )