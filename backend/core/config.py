"""
应用配置模块
使用 pydantic-settings 从 .env 文件读取配置
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库连接地址
    DATABASE_URL: str = "sqlite+aiosqlite:///./novel_tag.db"
    # Redis 连接地址
    REDIS_URL: str = ""
    # 文件上传目录
    UPLOAD_DIR: str = "./uploads"
    # 最大上传文件大小（MB）
    MAX_UPLOAD_SIZE_MB: int = 200
    # 默认摘要长度（字数）
    DEFAULT_SUMMARY_LENGTH: int = 100
    # API Key 加密密钥（32字节十六进制）
    ENCRYPTION_KEY: str = "0123456789abcdef0123456789abcdef"
    # 服务器主机地址
    HOST: str = "0.0.0.0"
    # 服务器端口
    PORT: int = 8000
    # 长文本分块大小（字符数）
    CHUNK_SIZE: int = 8000
    # 分块重叠字符数，保证上下文连贯
    CHUNK_OVERLAP: int = 500

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# 全局配置单例
settings = Settings()
