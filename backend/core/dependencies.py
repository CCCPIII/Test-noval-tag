"""
公共依赖注入模块
集中导出常用依赖，方便路由层引用
"""

from backend.core.database import get_db
from backend.core.redis import get_redis

# 重新导出数据库和 Redis 依赖
__all__ = ["get_db", "get_redis", "get_current_user"]


async def get_current_user() -> dict:
    """
    获取当前用户（占位实现）
    TODO: 接入真实认证系统后替换
    """
    return {"user_id": 1}
