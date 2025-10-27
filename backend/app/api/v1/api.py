"""
API v1 路由聚合
"""

from fastapi import APIRouter
from app.api.v1.endpoints import search, admin

api_router = APIRouter()

# 搜索相关API
api_router.include_router(
    search.router,
    prefix="/get-top3",
    tags=["search"]
)

# 管理员API
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)