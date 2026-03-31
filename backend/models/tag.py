"""
标签模型
存储所有标签，按维度分类
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, UniqueConstraint
from backend.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 标签名称
    name = Column(String(100), nullable=False)
    # 标签维度: genre(题材) / style(风格) / element(元素) / character(角色) / exclusive(独占)
    dimension = Column(String(20), nullable=False)
    # 是否为用户自定义标签
    is_custom = Column(Boolean, default=False)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("name", "dimension", name="uq_tag_name_dimension"),
    )
