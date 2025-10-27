"""
应用配置设置
"""

from typing import List, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """应用配置类"""

    # 基础配置
    APP_NAME: str = "Top3-Hunter"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]

    # 数据库配置
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """验证数据库URL格式"""
        if not v.startswith(("postgresql://", "sqlite:///")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite URL")
        return v

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # API密钥配置
    SERPER_API_KEY: str
    LLM_API_KEY: str
    LLM_PROVIDER: str = "anthropic"  # anthropic 或 openai
    LLM_MODEL_NAME: str = "claude-3-haiku-20240307"

    @validator("LLM_PROVIDER")
    def validate_llm_provider(cls, v: str) -> str:
        """验证LLM提供商"""
        if v not in ["anthropic", "openai"]:
            raise ValueError("LLM_PROVIDER must be 'anthropic' or 'openai'")
        return v

    # 缓存配置
    CACHE_TTL_QUERY: int = 21600  # 6小时，查询结果缓存
    CACHE_TTL_CONFIG: int = 60    # 1分钟，配置缓存
    CACHE_PREFIX: str = "top3_hunter"

    # 管理员配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24小时

    # 外部API配置
    SEARCH_TIMEOUT: int = 30
    LLM_TIMEOUT: int = 60
    MAX_RETRIES: int = 3

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 安全配置
    CORS_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 常用配置常量
DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL

# API端点配置
API_V1_STR = "/api/v1"

# 分页配置
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 搜索配置
MAX_SEARCH_RESULTS = 10
TOP_PRODUCTS_COUNT = 3