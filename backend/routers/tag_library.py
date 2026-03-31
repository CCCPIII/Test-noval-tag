"""
标签库管理路由
提供标签库的增删改查、按维度分组查询、批量添加等接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db, get_current_user
from backend.schemas.tag_library import (
    TagLibraryCreate,
    TagLibraryUpdate,
    TagLibraryResponse,
    TagLibraryListResponse,
    TagLibraryBatchCreate,
)
from backend.services import tag_library_service

router = APIRouter(prefix="/tag-library", tags=["标签库管理"])


@router.get("/", response_model=TagLibraryListResponse, summary="获取标签库列表")
async def list_tag_library(
    dimension: Optional[str] = Query(None, description="按维度过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    分页查询标签库列表
    支持按维度过滤
    """
    try:
        items, total = await tag_library_service.list_entries(
            db=db,
            dimension=dimension,
            page=page,
            page_size=page_size,
        )
        return TagLibraryListResponse(total=total, items=items)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询标签库失败: {str(e)}",
        )


@router.get("/grouped", summary="按维度分组获取标签")
async def get_grouped_tags(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    按维度分组获取所有标签，用于前端下拉选择
    返回格式: { "genre": [...], "style": [...], ... }
    """
    try:
        grouped = await tag_library_service.get_grouped_by_dimension(db)
        return grouped

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取分组标签失败: {str(e)}",
        )


@router.post("/", response_model=TagLibraryResponse, status_code=status.HTTP_201_CREATED, summary="添加标签到标签库")
async def create_tag_library_entry(
    data: TagLibraryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    向标签库中添加一个新标签
    """
    try:
        entry = await tag_library_service.create_entry(db, data)
        await db.commit()
        await db.refresh(entry)
        return entry

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"添加标签失败: {str(e)}",
        )


@router.post("/batch", response_model=list[TagLibraryResponse], status_code=status.HTTP_201_CREATED, summary="批量添加标签")
async def batch_create_tag_library(
    data: TagLibraryBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    批量向标签库中添加多个标签
    """
    try:
        entries = await tag_library_service.batch_create_entries(db, data.tags)
        await db.commit()
        return entries

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量添加标签失败: {str(e)}",
        )


@router.put("/{entry_id}", response_model=TagLibraryResponse, summary="更新标签库条目")
async def update_tag_library_entry(
    entry_id: int,
    data: TagLibraryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    更新标签库中的指定条目
    """
    try:
        entry = await tag_library_service.update_entry(db, entry_id, data)
        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"标签库条目不存在（ID: {entry_id}）",
            )
        await db.commit()
        await db.refresh(entry)
        return entry

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新标签失败: {str(e)}",
        )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除标签库条目")
async def delete_tag_library_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    从标签库中删除指定条目
    """
    try:
        success = await tag_library_service.delete_entry(db, entry_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"标签库条目不存在（ID: {entry_id}）",
            )
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除标签失败: {str(e)}",
        )
