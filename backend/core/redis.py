"""
Redis 连接模块
提供异步 Redis 连接的初始化、关闭和依赖注入
"""

import redis.asyncio as aioredis
from typing import Optional

from backend.core.config import settings

# 全局 Redis 连接实例
_redis: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    """初始化 Redis 连接"""
    global _redis
    _redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis() -> None:
    """关闭 Redis 连接"""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None


async def get_redis() -> aioredis.Redis:
    """获取 Redis 连接的依赖注入"""
    if _redis is None:
        await init_redis()
    return _redis
