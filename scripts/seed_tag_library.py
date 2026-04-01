"""
传统标签库初始化种子数据
运行方式: python -m scripts.seed_tag_library
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import async_session, init_db
from backend.models.tag_library import TagLibrary
from sqlalchemy import select

# 传统标签库种子数据 - 与 backend/services/tag_library_seed.py 保持同步
from backend.services.tag_library_seed import SEED_DATA


async def seed():
    """向数据库插入种子数据"""
    await init_db()

    async with async_session() as session:
        count = 0
        for dimension, tags in SEED_DATA.items():
            for sort_idx, (name, desc) in enumerate(tags):
                # 检查是否已存在
                result = await session.execute(
                    select(TagLibrary).where(
                        TagLibrary.name == name,
                        TagLibrary.dimension == dimension
                    )
                )
                if result.scalar_one_or_none():
                    continue

                entry = TagLibrary(
                    name=name,
                    dimension=dimension,
                    description=desc,
                    sort_order=sort_idx
                )
                session.add(entry)
                count += 1

        await session.commit()
        print(f"成功插入 {count} 条标签库种子数据")


if __name__ == "__main__":
    asyncio.run(seed())
