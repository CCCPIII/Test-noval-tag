"""
AI 模型配置
存储各 AI 模型的接口地址、密钥和能力参数
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime
from backend.core.database import Base


class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 模型显示名称
    name = Column(String(100), nullable=False, unique=True)
    # 模型提供商: openai / zhipu / local / custom
    provider = Column(String(50), nullable=False)
    # API 接口地址
    api_url = Column(String(500), nullable=False)
    # 加密存储的 API Key
    api_key_encrypted = Column(String(500), nullable=True)
    # 模型标识符（如 gpt-4, glm-4 等）
    model_identifier = Column(String(200), nullable=False)
    # 是否启用
    is_active = Column(Boolean, default=True)
    # 最大 token 数
    max_tokens = Column(Integer, default=4096)
    # 模型描述
    description = Column(String(1000), nullable=True)
    # 该模型适合处理的最大字符数
    supported_max_chars = Column(BigInteger, nullable=True)
    # 平均速度评级: fast / medium / slow
    avg_speed = Column(String(50), nullable=True)
    # 准确度备注
    accuracy_note = Column(String(200), nullable=True)
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
