"""
Redis 连接模块
提供异步 Redis 连接的初始化、关闭和依赖注入
Redis 为可选依赖，未配置或连接失败时自动降级为无缓存模式
"""

import logging
from typing import Optional

from backend.core.config import settings

logger = logging.getLogger(__name__)

# 全局 Redis 连接实例
_redis = None
_redis_available = False


async def init_redis() -> None:
    """初始化 Redis 连接，失败时静默降级"""
    global _redis, _redis_available
    if not settings.REDIS_URL:
        logger.info("REDIS_URL 未配置，跳过 Redis 初始化")
        return
    try:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis.ping()
        _redis_available = True
        logger.info("Redis 连接成功")
    except Exception as e:
        logger.warning(f"Redis 连接失败，将以无缓存模式运行: {e}")
        _redis = None
        _redis_available = False


async def close_redis() -> None:
    """关闭 Redis 连接"""
    global _redis, _redis_available
    if _redis is not None:
        try:
            await _redis.close()
        except Exception:
            pass
        _redis = None
        _redis_available = False


async def get_redis():
    """获取 Redis 连接，不可用时返回 None"""
    return _redis if _redis_available else None
