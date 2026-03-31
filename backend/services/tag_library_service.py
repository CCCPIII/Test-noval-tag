"""
标签库管理服务
管理预定义标签库的增删改查，按维度分组查询
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.tag_library import TagLibrary


async def create_tag_library_entry(
    db: AsyncSession,
    name: str,
    dimension: str,
    description: Optional[str] = None,
    sort_order: int = 0,
) -> TagLibrary:
    """
    添加一条标签库记录
    标签库用于维护预定义的可选标签列表，供 AI 和用户参考
    """
    entry = TagLibrary(
        name=name,
        dimension=dimension,
        description=description,
        sort_order=sort_order,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


async def update_tag_library_entry(
    db: AsyncSession,
    entry_id: int,
    **kwargs,
) -> Optional[TagLibrary]:
    """
    更新标签库条目
    支持部分字段更新，仅更新传入的非 None 字段
    """
    stmt = select(TagLibrary).where(TagLibrary.id == entry_id)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        return None

    # 动态更新传入的字段
    allowed_fields = {"name", "dimension", "description", "sort_order"}
    for key, value in kwargs.items():
        if key in allowed_fields and value is not None:
            setattr(entry, key, value)

    await db.flush()
    await db.refresh(entry)
    return entry


async def delete_tag_library_entry(db: AsyncSession, entry_id: int) -> bool:
    """
    删除标签库条目
    """
    stmt = select(TagLibrary).where(TagLibrary.id == entry_id)
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        return False

    await db.delete(entry)
    await db.flush()
    return True


async def list_tag_library(
    db: AsyncSession,
    dimension_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple:
    """
    分页查询标签库列表

    Args:
        db: 数据库会话
        dimension_filter: 可选的维度过滤（genre/style/element/character/exclusive）
        page: 页码
        page_size: 每页条数

    Returns:
        (标签列表, 总数)
    """
    base_query = select(TagLibrary)
    count_query = select(func.count(TagLibrary.id))

    if dimension_filter:
        base_query = base_query.where(TagLibrary.dimension == dimension_filter)
        count_query = count_query.where(TagLibrary.dimension == dimension_filter)

    # 查询总数
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询，按维度和排序权重排列
    offset = (page - 1) * page_size
    stmt = (
        base_query
        .order_by(TagLibrary.dimension, TagLibrary.sort_order, TagLibrary.name)
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()

    return list(entries), total


async def get_all_tags_by_dimension(db: AsyncSession) -> dict:
    """
    按维度分组返回所有标签库条目
    供 AI 生成标签时作为参考词表

    Returns:
        {
            "genre": [{"name": "...", "description": "..."}, ...],
            "style": [...],
            ...
        }
    """
    stmt = select(TagLibrary).order_by(TagLibrary.dimension, TagLibrary.sort_order)
    result = await db.execute(stmt)
    entries = result.scalars().all()

    grouped: dict = {}
    for entry in entries:
        if entry.dimension not in grouped:
            grouped[entry.dimension] = []
        grouped[entry.dimension].append({
            "name": entry.name,
            "description": entry.description or "",
        })

    return grouped


async def batch_create(db: AsyncSession, entries: List[dict]) -> list:
    """
    批量创建标签库条目
    每个条目应包含 name、dimension，可选 description 和 sort_order

    Args:
        entries: 标签条目字典列表

    Returns:
        创建成功的 TagLibrary 对象列表
    """
    created = []
    for entry_data in entries:
        entry = TagLibrary(
            name=entry_data["name"],
            dimension=entry_data["dimension"],
            description=entry_data.get("description"),
            sort_order=entry_data.get("sort_order", 0),
        )
        db.add(entry)
        created.append(entry)

    await db.flush()
    # 刷新所有新建对象以获取自增 ID
    for entry in created:
        await db.refresh(entry)

    return created
