"""
小说模型
存储上传的小说基本信息和处理状态
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from backend.core.database import Base


class Novel(Base):
    __tablename__ = "novels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 小说标题
    title = Column(String(500), nullable=False)
    # 作者
    author = Column(String(200), nullable=True)
    # 文件存储路径
    file_path = Column(String(1000), nullable=True)
    # 文件 SHA-256 哈希，用于去重
    file_hash = Column(String(64), unique=True, index=True)
    # 文件大小（字节）
    file_size = Column(BigInteger, nullable=True)
    # 文本字符数
    char_count = Column(BigInteger, default=0)
    # 处理状态: uploaded / processing / done / error
    status = Column(String(20), default="uploaded")
    # 上传时间
    upload_time = Column(DateTime, default=datetime.utcnow)
    # 最后更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
