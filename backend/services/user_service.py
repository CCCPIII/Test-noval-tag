"""
用户服务（占位实现）
预留用户认证和收藏管理接口，待后续接入完整认证系统
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(db: AsyncSession, data: dict) -> dict:
    """
    创建用户（占位）
    TODO: 接入真实注册逻辑，包括密码哈希、邮箱验证等
    """
    return {
        "message": "用户注册功能暂未开放，预留接口",
        "user_id": None,
        "status": "not_implemented",
    }


async def login(db: AsyncSession, username: str, password: str) -> dict:
    """
    用户登录（占位）
    TODO: 接入真实认证逻辑，返回 JWT token
    """
    return {
        "message": "登录功能暂未开放，预留接口",
        "token": None,
        "status": "not_implemented",
    }


async def get_user(db: AsyncSession, user_id: int) -> dict:
    """
    获取用户信息（占位）
    TODO: 查询数据库返回用户详情
    """
    return {
        "message": "用户信息查询功能暂未开放，预留接口",
        "user_id": user_id,
        "status": "not_implemented",
    }


async def add_favorite(db: AsyncSession, user_id: int, novel_id: int) -> dict:
    """
    添加收藏（占位）
    TODO: 实现用户收藏小说的功能，需要新建收藏关联表
    """
    return {
        "message": "收藏功能暂未开放，预留接口",
        "user_id": user_id,
        "novel_id": novel_id,
        "status": "not_implemented",
    }


async def get_favorites(db: AsyncSession, user_id: int) -> list:
    """
    获取用户收藏列表（占位）
    TODO: 查询收藏关联表，返回用户收藏的小说列表
    """
    return []
