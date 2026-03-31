"""
标签库模型
预定义的标签库，用于管理可选标签列表
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from backend.core.database import Base


class TagLibrary(Base):
    __tablename__ = "tag_library"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 标签名称
    name = Column(String(100), nullable=False)
    # 标签维度: genre / style / element / character / exclusive
    dimension = Column(String(20), nullable=False)
    # 标签描述
    description = Column(String(500), nullable=True)
    # 排序权重，数值越小越靠前
    sort_order = Column(Integer, default=0)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("name", "dimension", name="uq_tag_library_name_dimension"),
    )
