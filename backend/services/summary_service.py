"""
摘要生成服务
负责调用 AI 模型对小说文本生成摘要，支持短文本直接生成和长文本分块后合并
"""

import json
import logging
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.novel import Novel
from backend.models.summary import Summary
from backend.models.ai_model import AIModel
from backend.services.chunking_service import chunk_text, TextChunk
from backend.services.file_parser import parse_txt

logger = logging.getLogger(__name__)

# 短文本阈值（字符数），低于此值直接生成摘要，无需分块
SHORT_TEXT_THRESHOLD = 8000


async def _get_novel_text(novel: Novel) -> str:
    """
    读取小说的完整文本内容
    优先从文件路径读取，文件不存在时返回空字符串
    """
    if novel.file_path:
        try:
            return parse_txt(novel.file_path)
        except Exception as e:
            logger.error(f"读取小说文件失败: {novel.file_path}, 错误: {e}")
            return ""
    return ""


async def _get_ai_model(db: AsyncSession, model_id: Optional[int]) -> Optional[AIModel]:
    """
    获取指定的 AI 模型配置；如未指定则获取第一个激活的模型
    """
    if model_id:
        stmt = select(AIModel).where(AIModel.id == model_id, AIModel.is_active == True)
    else:
        stmt = select(AIModel).where(AIModel.is_active == True).limit(1)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _single_pass_summary(ai_model: Optional[AIModel], text: str, target_length: int) -> str:
    """
    短文本单次摘要生成
    直接将全文发送给 AI 模型，获取目标长度的摘要
    """
    if not ai_model:
        return f"[AI 模型未配置] 原文共 {len(text)} 字，目标摘要长度 {target_length} 字。请先在系统中配置 AI 模型后重新生成。"

    try:
        from backend.ai.client_factory import create_ai_client
        from backend.ai.prompts import SUMMARY_PROMPT
        from backend.services.ai_model_service import _decrypt_api_key

        # 解密 API Key
        api_key = None
        if ai_model.api_key_encrypted:
            api_key = _decrypt_api_key(ai_model.api_key_encrypted)

        client = create_ai_client(
            provider=ai_model.provider,
            api_url=ai_model.api_url,
            api_key=api_key,
            model_identifier=ai_model.model_identifier,
            max_tokens=ai_model.max_tokens,
        )
        prompt = SUMMARY_PROMPT.format(text=text[:16000], length=target_length)
        result = await client.generate_text(prompt, max_tokens=target_length * 3)
        return result
    except Exception as e:
        logger.error(f"AI 摘要生成失败: {e}")
        return f"[摘要生成失败] 错误信息: {str(e)}"


async def _chunked_summary(
    ai_model: Optional[AIModel],
    chunks: List[TextChunk],
    target_length: int,
    redis,
    novel_id: int,
) -> str:
    """
    长文本分块摘要生成
    1. 对每个块分别生成摘要
    2. 在 Redis 中跟踪处理进度
    3. 所有块完成后，合并各块摘要生成最终摘要

    Args:
        ai_model: AI 模型配置
        chunks: 文本块列表
        target_length: 最终摘要目标长度
        redis: Redis 连接，用于进度追踪
        novel_id: 小说 ID，用于 Redis 进度 key
    """
    total_chunks = len(chunks)
    chunk_summaries = []

    # 在 Redis 中初始化进度信息
    progress_key = f"summary_progress:{novel_id}"
    if redis:
        try:
            await redis.set(progress_key, json.dumps({
                "total_chunks": total_chunks,
                "completed_chunks": 0,
                "status": "processing",
                "progress_percent": 0.0,
            }))
        except Exception:
            pass

    # 逐块生成摘要
    for i, chunk in enumerate(chunks):
        # 每个块的目标摘要长度按比例分配
        chunk_target = max(50, target_length // total_chunks)
        chunk_summary = await _single_pass_summary(ai_model, chunk.text, chunk_target)
        chunk_summaries.append(chunk_summary)

        # 更新 Redis 进度
        if redis:
            try:
                progress = (i + 1) / total_chunks * 100
                await redis.set(progress_key, json.dumps({
                    "total_chunks": total_chunks,
                    "completed_chunks": i + 1,
                    "status": "processing" if i + 1 < total_chunks else "merging",
                    "progress_percent": round(progress, 1),
                }))
            except Exception:
                pass

    # 合并所有块的摘要为最终摘要
    merged_text = "\n".join(chunk_summaries)
    final_summary = await _single_pass_summary(ai_model, merged_text, target_length)

    # 更新 Redis 进度为完成
    if redis:
        try:
            await redis.set(progress_key, json.dumps({
                "total_chunks": total_chunks,
                "completed_chunks": total_chunks,
                "status": "done",
                "progress_percent": 100.0,
            }))
        except Exception:
            pass

    return final_summary


async def generate_summary(
    db: AsyncSession,
    redis,
    novel_id: int,
    target_length: int = 100,
    model_id: Optional[int] = None,
) -> Optional[Summary]:
    """
    摘要生成主入口

    流程：
    1. 获取小说信息和文本
    2. 获取 AI 模型配置
    3. 根据文本长度选择单次生成或分块生成
    4. 将结果存入数据库

    Args:
        db: 数据库会话
        redis: Redis 连接
        novel_id: 小说 ID
        target_length: 目标摘要长度（字数）
        model_id: 指定 AI 模型 ID（可选）

    Returns:
        生成的 Summary 对象
    """
    # 获取小说记录
    stmt = select(Novel).where(Novel.id == novel_id)
    result = await db.execute(stmt)
    novel = result.scalar_one_or_none()
    if not novel:
        return None

    # 读取小说文本
    text = await _get_novel_text(novel)
    if not text:
        return None

    # 获取 AI 模型
    ai_model = await _get_ai_model(db, model_id)

    # 根据文本长度决定生成策略
    if len(text) <= SHORT_TEXT_THRESHOLD:
        # 短文本直接生成
        content = await _single_pass_summary(ai_model, text, target_length)
    else:
        # 长文本分块处理
        chunks = chunk_text(text)
        content = await _chunked_summary(ai_model, chunks, target_length, redis, novel_id)

    # 保存摘要到数据库
    summary = Summary(
        novel_id=novel_id,
        content=content,
        target_length=target_length,
        actual_length=len(content),
        model_used=ai_model.name if ai_model else "未配置",
        is_chunk_summary=False,
        chunk_index=None,
    )
    db.add(summary)
    await db.flush()
    await db.refresh(summary)
    return summary


async def update_summary(db: AsyncSession, summary_id: int, content: str) -> Optional[Summary]:
    """
    编辑已有摘要内容（用户手动修改）
    """
    stmt = select(Summary).where(Summary.id == summary_id)
    result = await db.execute(stmt)
    summary = result.scalar_one_or_none()
    if not summary:
        return None

    summary.content = content
    summary.actual_length = len(content)
    await db.flush()
    await db.refresh(summary)
    return summary


async def get_summaries(db: AsyncSession, novel_id: int) -> list:
    """
    获取某小说的所有最终摘要（排除分块中间摘要）
    按创建时间降序排列
    """
    stmt = (
        select(Summary)
        .where(Summary.novel_id == novel_id, Summary.is_chunk_summary == False)
        .order_by(Summary.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
