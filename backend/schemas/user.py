"""用户模块请求/响应模型（预留）"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """用户注册（预留）"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    email: Optional[str] = Field(None, max_length=200)


class UserLogin(BaseModel):
    """用户登录（预留）"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户信息响应（预留）"""
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class UserFavorite(BaseModel):
    """收藏操作（预留）"""
    novel_id: int
