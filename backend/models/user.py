"""
用户模型（占位）
TODO: 接入完整的用户认证系统
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 用户名
    username = Column(String(100), unique=True, nullable=False)
    # 密码哈希
    password_hash = Column(String(200), nullable=False)
    # 邮箱
    email = Column(String(200), nullable=True)
    # 是否激活
    is_active = Column(Boolean, default=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)
