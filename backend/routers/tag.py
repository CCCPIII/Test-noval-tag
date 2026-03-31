"""
标签管理路由
提供 AI 标签生成、标签查询、手动分配、批量分配、标签移除、争议标记等接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db, get_redis, get_current_user
from backend.schemas.tag import (
    TagResponse,
    TagAssign,
    TagBatchAssign,
    TagGenerateRequest,
    TagGenerateResponse,
)
from backend.schemas.novel import NovelTagResponse
from backend.services import novel_service, tag_service

router = APIRouter(prefix="/novels", tags=["标签管理"])


class ControversyUpdate(BaseModel):
    """争议标签更新请求"""
    is_controversial: bool = Field(..., description="是否为争议标签")
    controversy_note: Optional[str] = Field(None, max_length=200, description="争议说明（50字以内）")


@router.post(
    "/{novel_id}/tags/generate",
    response_model=TagGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI 生成标签",
)
async def generate_tags(
    novel_id: int,
    request: TagGenerateRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    """
    调用 AI 为指定小说自动生成标签
    - 校验小说是否存在
    - 调用 tag_service 生成标签
    - 返回生成的标签列表（含专属标签）
    """
    try:
        # 校验小说是否存在
        novel = await novel_service.get_novel(db, novel_id)
        if not novel:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        # 调用标签生成服务
        result = await tag_service.generate_tags(
            db=db,
            redis=redis,
            novel_id=novel_id,
            model_id=request.model_id,
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"标签生成失败: {str(e)}",
        )


@router.get("/{novel_id}/tags", response_model=list[NovelTagResponse], summary="获取小说的所有标签")
async def get_novel_tags(
    novel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    获取指定小说的所有关联标签
    包含标签维度、置信度、是否手动分配、是否争议等信息
    """
    try:
        # 校验小说是否存在
        novel = await novel_service.get_novel(db, novel_id)
        if not novel:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        tags = await tag_service.get_novel_tags(db, novel_id)
        return tags

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取标签失败: {str(e)}",
        )


@router.post("/{novel_id}/tags/assign", response_model=NovelTagResponse, summary="手动分配标签")
async def assign_tag(
    novel_id: int,
    data: TagAssign,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    手动为小说分配一个标签
    """
    try:
        # 校验小说是否存在
        novel = await novel_service.get_novel(db, novel_id)
        if not novel:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        result = await tag_service.assign_tag(
            db=db,
            novel_id=novel_id,
            tag_id=data.tag_id,
            is_manual=data.is_manual,
            is_controversial=data.is_controversial,
            controversy_note=data.controversy_note,
        )
        await db.commit()
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分配标签失败: {str(e)}",
        )


@router.post("/{novel_id}/tags/batch-assign", response_model=list[NovelTagResponse], summary="批量分配标签")
async def batch_assign_tags(
    novel_id: int,
    data: TagBatchAssign,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    批量为小说分配多个标签
    """
    try:
        # 校验小说是否存在
        novel = await novel_service.get_novel(db, novel_id)
        if not novel:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        results = await tag_service.batch_assign_tags(
            db=db,
            novel_id=novel_id,
            tags=data.tags,
        )
        await db.commit()
        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量分配标签失败: {str(e)}",
        )


@router.delete("/{novel_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="移除标签")
async def remove_tag(
    novel_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    从小说中移除指定标签
    """
    try:
        success = await tag_service.remove_tag(db, novel_id, tag_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"未找到小说（ID: {novel_id}）与标签（ID: {tag_id}）的关联",
            )
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"移除标签失败: {str(e)}",
        )


@router.put("/{novel_id}/tags/{tag_id}/controversy", response_model=NovelTagResponse, summary="更新争议标签状态")
async def update_controversy(
    novel_id: int,
    tag_id: int,
    data: ControversyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    标记/更新标签的争议状态
    - 设置是否为争议标签
    - 添加争议说明备注
    """
    try:
        result = await tag_service.update_controversy(
            db=db,
            novel_id=novel_id,
            tag_id=tag_id,
            is_controversial=data.is_controversial,
            controversy_note=data.controversy_note,
        )
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"未找到小说（ID: {novel_id}）与标签（ID: {tag_id}）的关联",
            )
        await db.commit()
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新争议状态失败: {str(e)}",
        )
