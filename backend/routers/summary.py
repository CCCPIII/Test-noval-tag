"""
总结生成路由
提供 AI 总结生成、总结列表查询、总结编辑、分段处理进度查询等接口
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db, get_redis, get_current_user
from backend.schemas.summary import (
    SummaryRequest,
    SummaryUpdate,
    SummaryResponse,
    ChunkProgressResponse,
)
from backend.services import novel_service, summary_service

router = APIRouter(prefix="/novels", tags=["总结生成"])


@router.post(
    "/{novel_id}/summary/generate",
    response_model=SummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="生成小说总结",
)
async def generate_summary(
    novel_id: int,
    request: SummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    为指定小说生成 AI 总结
    - 校验小说是否存在
    - 调用 summary_service 生成总结
    - 支持指定目标长度和 AI 模型
    """
    try:
        # 校验小说是否存在
        novel = await novel_service.get_novel(db, novel_id)
        if not novel:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        # 调用总结服务生成总结
        summary = await summary_service.generate_summary(
            db=db,
            novel_id=novel_id,
            target_length=request.target_length,
            model_id=request.model_id,
        )
        return summary

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成总结失败: {str(e)}",
        )


@router.get("/{novel_id}/summaries", response_model=list[SummaryResponse], summary="获取小说的所有总结")
async def get_novel_summaries(
    novel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    获取指定小说的所有总结记录
    按创建时间降序排列
    """
    try:
        # 校验小说是否存在
        novel = await novel_service.get_novel(db, novel_id)
        if not novel:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        # 获取总结列表
        summaries = await summary_service.get_summaries_by_novel(db, novel_id)
        return summaries

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取总结列表失败: {str(e)}",
        )


@router.put("/summaries/{summary_id}", response_model=SummaryResponse, summary="编辑总结")
async def update_summary(
    summary_id: int,
    data: SummaryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    编辑/更新已有的总结内容
    """
    try:
        summary = await summary_service.update_summary(
            db=db,
            summary_id=summary_id,
            content=data.content,
        )
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"总结不存在（ID: {summary_id}）",
            )
        await db.commit()
        await db.refresh(summary)
        return summary

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新总结失败: {str(e)}",
        )


@router.get("/{novel_id}/summary/progress", response_model=ChunkProgressResponse, summary="查询分段处理进度")
async def get_summary_progress(
    novel_id: int,
    redis=Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    """
    查询长篇小说分段总结的处理进度
    进度信息存储在 Redis 中
    """
    try:
        # 从 Redis 获取进度信息
        progress_key = f"summary_progress:{novel_id}"
        progress_data = await redis.get(progress_key)

        if not progress_data:
            raise HTTPException(
                status_code=404,
                detail=f"未找到小说（ID: {novel_id}）的处理进度信息",
            )

        progress = json.loads(progress_data)
        return ChunkProgressResponse(
            novel_id=novel_id,
            total_chunks=progress.get("total_chunks", 0),
            completed_chunks=progress.get("completed_chunks", 0),
            status=progress.get("status", "unknown"),
            progress_percent=progress.get("progress_percent", 0.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询进度失败: {str(e)}",
        )
