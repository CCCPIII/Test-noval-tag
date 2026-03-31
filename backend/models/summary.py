"""
摘要模型
存储 AI 生成的小说摘要，支持分段摘要
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from backend.core.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 关联小说 ID
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    # 摘要正文
    content = Column(Text, nullable=False)
    # 目标摘要长度（字数）
    target_length = Column(Integer, nullable=True)
    # 实际摘要长度（字数）
    actual_length = Column(Integer, nullable=True)
    # 使用的 AI 模型名称
    model_used = Column(String(100), nullable=True)
    # 是否为分段摘要（长文本分块处理时的中间结果）
    is_chunk_summary = Column(Boolean, default=False)
    # 分块索引，仅分段摘要时有值
    chunk_index = Column(Integer, nullable=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)
