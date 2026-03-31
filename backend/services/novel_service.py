"""
小说 CRUD 服务
提供小说的创建、查询、列表、状态更新、删除等操作
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.novel import Novel
from backend.models.summary import Summary
from backend.models.tag import Tag
from backend.models.novel_tag import NovelTag


async def create_novel(
    db: AsyncSession,
    title: str,
    author: Optional[str],
    file_path: Optional[str],
    file_hash: str,
    file_size: Optional[int],
    char_count: int,
) -> Novel:
    """
    创建小说记录
    将上传/输入的小说信息写入数据库
    """
    novel = Novel(
        title=title,
        author=author,
        file_path=file_path,
        file_hash=file_hash,
        file_size=file_size,
        char_count=char_count,
        status="uploaded",
    )
    db.add(novel)
    await db.flush()
    await db.refresh(novel)
    return novel


async def get_novel(db: AsyncSession, novel_id: int) -> Optional[Novel]:
    """
    根据 ID 获取单个小说记录
    """
    stmt = select(Novel).where(Novel.id == novel_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_novels(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
) -> tuple:
    """
    分页查询小说列表

    Args:
        db: 数据库会话
        page: 页码，从 1 开始
        page_size: 每页数量
        status_filter: 可选的状态过滤条件

    Returns:
        (小说列表, 总数) 元组
    """
    # 构建基础查询
    base_query = select(Novel)
    count_query = select(func.count(Novel.id))

    # 添加状态过滤
    if status_filter:
        base_query = base_query.where(Novel.status == status_filter)
        count_query = count_query.where(Novel.status == status_filter)

    # 查询总数
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询，按上传时间降序排列
    offset = (page - 1) * page_size
    stmt = base_query.order_by(Novel.upload_time.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    novels = result.scalars().all()

    return list(novels), total


async def update_novel_status(db: AsyncSession, novel_id: int, status: str) -> Optional[Novel]:
    """
    更新小说的处理状态
    状态包括: uploaded / processing / done / error
    """
    novel = await get_novel(db, novel_id)
    if not novel:
        return None
    novel.status = status
    await db.flush()
    await db.refresh(novel)
    return novel


async def delete_novel(db: AsyncSession, novel_id: int) -> bool:
    """
    删除小说及其关联数据（摘要、标签关联）
    """
    novel = await get_novel(db, novel_id)
    if not novel:
        return False

    # 删除关联的摘要
    stmt = select(Summary).where(Summary.novel_id == novel_id)
    result = await db.execute(stmt)
    for summary in result.scalars().all():
        await db.delete(summary)

    # 删除关联的标签关系
    stmt = select(NovelTag).where(NovelTag.novel_id == novel_id)
    result = await db.execute(stmt)
    for novel_tag in result.scalars().all():
        await db.delete(novel_tag)

    # 删除小说本身
    await db.delete(novel)
    await db.flush()
    return True


async def get_novel_detail(db: AsyncSession, novel_id: int) -> Optional[dict]:
    """
    获取小说详情，包含摘要列表和标签列表

    Returns:
        包含 novel、summaries、tags 的字典，未找到时返回 None
    """
    novel = await get_novel(db, novel_id)
    if not novel:
        return None

    # 查询该小说的所有摘要（排除中间分块摘要）
    summary_stmt = (
        select(Summary)
        .where(Summary.novel_id == novel_id, Summary.is_chunk_summary == False)
        .order_by(Summary.created_at.desc())
    )
    summary_result = await db.execute(summary_stmt)
    summaries = summary_result.scalars().all()

    # 查询该小说的所有标签，关联标签表获取标签名和维度
    tag_stmt = (
        select(NovelTag, Tag)
        .join(Tag, NovelTag.tag_id == Tag.id)
        .where(NovelTag.novel_id == novel_id)
        .order_by(Tag.dimension, Tag.name)
    )
    tag_result = await db.execute(tag_stmt)
    tag_rows = tag_result.all()

    tags = []
    for novel_tag, tag in tag_rows:
        tags.append({
            "tag_id": tag.id,
            "tag_name": tag.name,
            "dimension": tag.dimension,
            "confidence": novel_tag.confidence,
            "is_manual": novel_tag.is_manual,
            "is_controversial": novel_tag.is_controversial,
            "controversy_note": novel_tag.controversy_note,
        })

    return {
        "novel": novel,
        "summaries": list(summaries),
        "tags": tags,
    }
