"""
小说-标签关联模型
存储小说与标签的多对多关系，包含置信度和争议标记
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from backend.core.database import Base


class NovelTag(Base):
    __tablename__ = "novel_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 关联小说 ID
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    # 关联标签 ID
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    # AI 预测置信度（0-1）
    confidence = Column(Float, nullable=True)
    # 是否为用户手动添加
    is_manual = Column(Boolean, default=False)
    # 是否存在争议（AI 不确定时标记）
    is_controversial = Column(Boolean, default=False)
    # 争议说明，鼠标悬停时显示
    controversy_note = Column(String(200), nullable=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)
