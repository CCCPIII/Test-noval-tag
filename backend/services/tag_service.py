"""
标签生成服务
负责调用 AI 模型为小说生成多维度标签，并管理标签的增删查
"""

import json
import logging
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.novel import Novel
from backend.models.tag import Tag
from backend.models.novel_tag import NovelTag
from backend.models.ai_model import AIModel
from backend.services.chunking_service import chunk_text
from backend.services.file_parser import parse_txt

logger = logging.getLogger(__name__)

# 标签维度列表
TAG_DIMENSIONS = ["genre", "style", "element", "character", "exclusive"]


async def _get_novel_text(novel: Novel) -> str:
    """
    读取小说文本内容
    """
    if novel.file_path:
        try:
            return parse_txt(novel.file_path)
        except Exception as e:
            logger.error(f"读取小说文件失败: {novel.file_path}, 错误: {e}")
            return ""
    return ""


async def _extract_or_create_tag(
    db: AsyncSession,
    name: str,
    dimension: str,
    is_custom: bool = False,
) -> Tag:
    """
    查找已有标签或创建新标签
    根据名称和维度联合查询，不存在则新建
    """
    stmt = select(Tag).where(and_(Tag.name == name, Tag.dimension == dimension))
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()

    if tag:
        return tag

    # 创建新标签
    tag = Tag(name=name, dimension=dimension, is_custom=is_custom)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


async def _call_ai_for_tags(ai_model: Optional[AIModel], text: str) -> List[dict]:
    """
    调用 AI 模型提取标签
    返回格式: [{"name": "...", "dimension": "...", "confidence": 0.9}, ...]

    如果 AI 未配置，返回占位标签
    """
    if not ai_model:
        # AI 未配置时返回占位标签
        return [
            {"name": "待生成", "dimension": "genre", "confidence": 0.0},
            {"name": "待生成", "dimension": "style", "confidence": 0.0},
        ]

    try:
        # TODO: 根据 ai_model.provider 调用对应的 AI 接口
        # 提示词应要求 AI 按维度返回 JSON 格式的标签列表
        # 目前返回占位数据
        return [
            {"name": "待接入AI", "dimension": "genre", "confidence": 0.0},
            {"name": "待接入AI", "dimension": "style", "confidence": 0.0},
        ]
    except Exception as e:
        logger.error(f"AI 标签生成失败: {e}")
        return []


async def generate_tags(
    db: AsyncSession,
    redis,
    novel_id: int,
    model_id: Optional[int] = None,
) -> list:
    """
    为小说生成 AI 标签（主入口）

    流程：
    1. 读取小说文本
    2. 如果是长文本，分块处理后合并标签结果
    3. 对每个标签查找或创建 Tag 记录
    4. 建立 NovelTag 关联关系

    Args:
        db: 数据库会话
        redis: Redis 连接（用于进度追踪）
        novel_id: 小说 ID
        model_id: 指定 AI 模型 ID

    Returns:
        生成的标签列表（包含维度和置信度信息）
    """
    # 获取小说记录
    stmt = select(Novel).where(Novel.id == novel_id)
    result = await db.execute(stmt)
    novel = result.scalar_one_or_none()
    if not novel:
        return []

    # 读取文本
    text = await _get_novel_text(novel)
    if not text:
        return []

    # 获取 AI 模型
    ai_model = None
    if model_id:
        stmt = select(AIModel).where(AIModel.id == model_id, AIModel.is_active == True)
    else:
        stmt = select(AIModel).where(AIModel.is_active == True).limit(1)
    result = await db.execute(stmt)
    ai_model = result.scalar_one_or_none()

    # 根据文本长度决定处理策略
    if len(text) <= 8000:
        # 短文本直接处理
        raw_tags = await _call_ai_for_tags(ai_model, text)
    else:
        # 长文本分块处理，收集各块的标签后去重合并
        chunks = chunk_text(text)
        all_raw_tags = []

        # 在 Redis 中追踪进度
        progress_key = f"tag_progress:{novel_id}"
        for i, chunk in enumerate(chunks):
            chunk_tags = await _call_ai_for_tags(ai_model, chunk.text)
            all_raw_tags.extend(chunk_tags)

            if redis:
                try:
                    progress = (i + 1) / len(chunks) * 100
                    await redis.set(progress_key, json.dumps({
                        "total_chunks": len(chunks),
                        "completed_chunks": i + 1,
                        "status": "processing" if i + 1 < len(chunks) else "merging",
                        "progress_percent": round(progress, 1),
                    }))
                except Exception:
                    pass

        # 按名称+维度去重，保留最高置信度
        tag_map = {}
        for t in all_raw_tags:
            key = (t["name"], t["dimension"])
            if key not in tag_map or t.get("confidence", 0) > tag_map[key].get("confidence", 0):
                tag_map[key] = t
        raw_tags = list(tag_map.values())

    # 将 AI 返回的标签存入数据库
    created_tags = []
    for tag_data in raw_tags:
        tag_name = tag_data.get("name", "").strip()
        dimension = tag_data.get("dimension", "genre")
        confidence = tag_data.get("confidence", 0.0)

        if not tag_name or dimension not in TAG_DIMENSIONS:
            continue

        # 查找或创建标签
        tag = await _extract_or_create_tag(db, tag_name, dimension)

        # 检查是否已关联，避免重复
        exist_stmt = select(NovelTag).where(
            and_(NovelTag.novel_id == novel_id, NovelTag.tag_id == tag.id)
        )
        exist_result = await db.execute(exist_stmt)
        if exist_result.scalar_one_or_none():
            continue

        # 创建关联关系
        novel_tag = NovelTag(
            novel_id=novel_id,
            tag_id=tag.id,
            confidence=confidence,
            is_manual=False,
            is_controversial=confidence < 0.5,  # 低置信度标记为争议
            controversy_note="AI 置信度较低，建议人工确认" if confidence < 0.5 else None,
        )
        db.add(novel_tag)
        await db.flush()

        created_tags.append({
            "tag_id": tag.id,
            "tag_name": tag.name,
            "dimension": tag.dimension,
            "confidence": confidence,
            "is_controversial": novel_tag.is_controversial,
        })

    # 更新 Redis 进度为完成
    if redis:
        try:
            await redis.set(f"tag_progress:{novel_id}", json.dumps({
                "status": "done",
                "progress_percent": 100.0,
            }))
        except Exception:
            pass

    return created_tags


async def assign_tag(
    db: AsyncSession,
    novel_id: int,
    tag_id: int,
    is_manual: bool = True,
    is_controversial: bool = False,
    controversy_note: Optional[str] = None,
) -> Optional[NovelTag]:
    """
    手动为小说分配标签
    如果该标签已关联则跳过
    """
    # 检查小说和标签是否存在
    novel = await db.execute(select(Novel).where(Novel.id == novel_id))
    if not novel.scalar_one_or_none():
        return None
    tag = await db.execute(select(Tag).where(Tag.id == tag_id))
    if not tag.scalar_one_or_none():
        return None

    # 检查是否已关联
    stmt = select(NovelTag).where(
        and_(NovelTag.novel_id == novel_id, NovelTag.tag_id == tag_id)
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    # 创建关联
    novel_tag = NovelTag(
        novel_id=novel_id,
        tag_id=tag_id,
        is_manual=is_manual,
        is_controversial=is_controversial,
        controversy_note=controversy_note,
    )
    db.add(novel_tag)
    await db.flush()
    await db.refresh(novel_tag)
    return novel_tag


async def remove_tag(db: AsyncSession, novel_id: int, tag_id: int) -> bool:
    """
    移除小说与标签的关联
    """
    stmt = select(NovelTag).where(
        and_(NovelTag.novel_id == novel_id, NovelTag.tag_id == tag_id)
    )
    result = await db.execute(stmt)
    novel_tag = result.scalar_one_or_none()
    if not novel_tag:
        return False

    await db.delete(novel_tag)
    await db.flush()
    return True


async def get_novel_tags(db: AsyncSession, novel_id: int) -> list:
    """
    获取小说的所有标签，包含维度信息
    通过 JOIN 查询同时获取 Tag 和 NovelTag 的信息
    """
    stmt = (
        select(NovelTag, Tag)
        .join(Tag, NovelTag.tag_id == Tag.id)
        .where(NovelTag.novel_id == novel_id)
        .order_by(Tag.dimension, Tag.name)
    )
    result = await db.execute(stmt)
    rows = result.all()

    tags = []
    for novel_tag, tag in rows:
        tags.append({
            "tag_id": tag.id,
            "tag_name": tag.name,
            "dimension": tag.dimension,
            "confidence": novel_tag.confidence,
            "is_manual": novel_tag.is_manual,
            "is_controversial": novel_tag.is_controversial,
            "controversy_note": novel_tag.controversy_note,
        })

    return tags
