"""
搜索服务
支持按小说名称搜索和按标签组合搜索两种模式
"""

from typing import Optional, List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.novel import Novel
from backend.models.tag import Tag
from backend.models.novel_tag import NovelTag
from backend.models.summary import Summary


async def _build_search_result(novels: list, db: AsyncSession) -> list:
    """
    丰富搜索结果，为每个小说附加摘要预览和标签名称

    对每本小说查询最新摘要（截取前 100 字作为预览）和所有标签名
    """
    results = []
    for novel in novels:
        # 获取最新摘要预览
        summary_stmt = (
            select(Summary)
            .where(Summary.novel_id == novel.id, Summary.is_chunk_summary == False)
            .order_by(Summary.created_at.desc())
            .limit(1)
        )
        summary_result = await db.execute(summary_stmt)
        summary = summary_result.scalar_one_or_none()
        summary_preview = ""
        if summary:
            # 截取前 100 字作为预览
            summary_preview = summary.content[:100] + ("..." if len(summary.content) > 100 else "")

        # 获取标签列表
        tag_stmt = (
            select(Tag)
            .join(NovelTag, NovelTag.tag_id == Tag.id)
            .where(NovelTag.novel_id == novel.id)
            .order_by(Tag.dimension, Tag.name)
        )
        tag_result = await db.execute(tag_stmt)
        tags = tag_result.scalars().all()

        results.append({
            "id": novel.id,
            "title": novel.title,
            "author": novel.author,
            "char_count": novel.char_count,
            "status": novel.status,
            "upload_time": novel.upload_time,
            "summary_preview": summary_preview,
            "tags": [{"id": t.id, "name": t.name, "dimension": t.dimension} for t in tags],
        })

    return results


async def search_by_name(
    db: AsyncSession,
    keyword: str,
    exact_match: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> tuple:
    """
    按小说名称搜索

    Args:
        db: 数据库会话
        keyword: 搜索关键词
        exact_match: 是否精确匹配（True=完全匹配，False=模糊搜索 LIKE）
        page: 页码
        page_size: 每页数量

    Returns:
        (搜索结果列表, 总数)
    """
    if exact_match:
        # 精确匹配
        filter_cond = Novel.title == keyword
    else:
        # 模糊搜索，支持标题和作者
        filter_cond = Novel.title.like(f"%{keyword}%")

    # 查询总数
    count_stmt = select(func.count(Novel.id)).where(filter_cond)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * page_size
    query_stmt = (
        select(Novel)
        .where(filter_cond)
        .order_by(Novel.upload_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query_stmt)
    novels = result.scalars().all()

    # 丰富搜索结果
    enriched = await _build_search_result(list(novels), db)
    return enriched, total


async def search_by_tags(
    db: AsyncSession,
    tag_ids: List[int],
    match_all: bool = True,
    page: int = 1,
    page_size: int = 20,
) -> tuple:
    """
    按标签组合搜索小说

    Args:
        db: 数据库会话
        tag_ids: 标签 ID 列表
        match_all: True=必须包含所有指定标签（AND），False=包含任一即可（OR）
        page: 页码
        page_size: 每页数量

    Returns:
        (搜索结果列表, 总数)

    实现思路：
    - match_all=True 时使用 GROUP BY + HAVING COUNT = len(tag_ids) 取交集
    - match_all=False 时使用 DISTINCT 取并集
    """
    if not tag_ids:
        return [], 0

    if match_all:
        # 交集查询：小说必须包含所有指定标签
        # SELECT novel_id FROM novel_tags WHERE tag_id IN (...) GROUP BY novel_id HAVING COUNT(DISTINCT tag_id) = N
        subquery = (
            select(NovelTag.novel_id)
            .where(NovelTag.tag_id.in_(tag_ids))
            .group_by(NovelTag.novel_id)
            .having(func.count(func.distinct(NovelTag.tag_id)) == len(tag_ids))
        ).subquery()
    else:
        # 并集查询：小说包含任意一个指定标签即可
        subquery = (
            select(func.distinct(NovelTag.novel_id).label("novel_id"))
            .where(NovelTag.tag_id.in_(tag_ids))
        ).subquery()

    # 查询总数
    count_stmt = select(func.count()).select_from(subquery)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 分页查询小说详情
    offset = (page - 1) * page_size
    query_stmt = (
        select(Novel)
        .where(Novel.id.in_(select(subquery.c.novel_id)))
        .order_by(Novel.upload_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query_stmt)
    novels = result.scalars().all()

    # 丰富搜索结果
    enriched = await _build_search_result(list(novels), db)
    return enriched, total
