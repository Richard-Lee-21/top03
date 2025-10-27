"""
Redis缓存管理
"""

import json
import logging
from typing import Any, Optional, Union
import aioredis
from aioredis import Redis

from app.core.config import settings
from app.core.exceptions import CacheError

logger = logging.getLogger(__name__)

# Redis连接池
redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """获取Redis客户端"""
    global redis_client

    if redis_client is None:
        try:
            redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )

            # 测试连接
            await redis_client.ping()
            logger.info("Redis connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise CacheError(f"Redis连接失败: {e}")

    return redis_client


async def close_redis():
    """关闭Redis连接"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")


class CacheService:
    """缓存服务类"""

    def __init__(self):
        self.prefix = settings.CACHE_PREFIX

    def _make_key(self, key: str) -> str:
        """生成带前缀的缓存键"""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            redis = await get_redis()
            cache_key = self._make_key(key)
            value = await redis.get(cache_key)

            if value:
                return json.loads(value)
            return None

        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        try:
            redis = await get_redis()
            cache_key = self._make_key(key)
            serialized_value = json.dumps(value, ensure_ascii=False)

            if ttl:
                await redis.setex(cache_key, ttl, serialized_value)
            else:
                await redis.set(cache_key, serialized_value)

            return True

        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            redis = await get_redis()
            cache_key = self._make_key(key)
            result = await redis.delete(cache_key)
            return result > 0

        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            redis = await get_redis()
            cache_key = self._make_key(key)
            result = await redis.exists(cache_key)
            return result > 0

        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的所有缓存"""
        try:
            redis = await get_redis()
            cache_pattern = self._make_key(pattern)
            keys = await redis.keys(cache_pattern)

            if keys:
                result = await redis.delete(*keys)
                logger.info(f"Cleared {result} cache entries matching pattern '{pattern}'")
                return result

            return 0

        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern '{pattern}': {e}")
            return 0

    async def get_ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        try:
            redis = await get_redis()
            cache_key = self._make_key(key)
            return await redis.ttl(cache_key)

        except Exception as e:
            logger.error(f"Cache TTL error for key '{key}': {e}")
            return -1

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """递增缓存值"""
        try:
            redis = await get_redis()
            cache_key = self._make_key(key)
            return await redis.incrby(cache_key, amount)

        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            return None

    async def health_check() -> bool:
        """Redis健康检查"""
        try:
            redis = await get_redis()
            await redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# 创建全局缓存服务实例
cache_service = CacheService()


# 缓存装饰器
def cache(key_template: str, ttl: int = settings.CACHE_TTL_QUERY):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = key_template.format(*args, **kwargs)

            # 尝试从缓存获取
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # 执行原函数
            result = await func(*args, **kwargs)

            # 存入缓存
            await cache_service.set(cache_key, result, ttl)
            logger.debug(f"Cache set for key: {cache_key}, TTL: {ttl}s")

            return result

        return wrapper
    return decorator