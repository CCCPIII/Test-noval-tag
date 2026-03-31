"""
模型汇总导出
确保所有模型在 Base.metadata 中注册，以便 init_db() 能正确建表
"""

from backend.models.novel import Novel
from backend.models.summary import Summary
from backend.models.tag import Tag
from backend.models.novel_tag import NovelTag
from backend.models.tag_library import TagLibrary
from backend.models.ai_model import AIModel
from backend.models.user import User

__all__ = [
    "Novel",
    "Summary",
    "Tag",
    "NovelTag",
    "TagLibrary",
    "AIModel",
    "User",
]
