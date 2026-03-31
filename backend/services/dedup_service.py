"""
文件去重服务
通过 SHA-256 哈希值判断小说是否已存在，避免重复上传
"""

import hashlib
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.novel import Novel


def compute_file_hash(file_path: str) -> str:
    """
    计算文件内容的 SHA-256 哈希值
    使用分块读取，避免大文件占用过多内存
    """
    sha256 = hashlib.sha256()
    # 分块读取文件，每次读取 8KB
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_text_hash(text: str) -> str:
    """
    计算文本内容的 SHA-256 哈希值
    用于手动输入文本时的去重判断
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def check_duplicate(db: AsyncSession, file_hash: str) -> Optional[Novel]:
    """
    查询数据库中是否已存在相同哈希值的小说记录
    如果存在则返回该小说对象，否则返回 None
    """
    stmt = select(Novel).where(Novel.file_hash == file_hash)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
