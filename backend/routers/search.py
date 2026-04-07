"""
搜索路由
提供按小说名称搜索和按标签搜索的接口
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db, get_current_user
from backend.schemas.search import SearchResponse, SearchMode
from backend.services import search_service

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("/by-name", response_model=SearchResponse, summary="按名称搜索小说")
async def search_by_name(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    exact_match: bool = Query(False, description="是否精准匹配"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    按小说名称搜索
    - 支持模糊匹配和精准匹配
    - 返回匹配的小说列表，包含总结预览和标签
    """
    try:
        items, total = await search_service.search_by_name(
            db=db,
            keyword=keyword,
            exact_match=exact_match,
            page=page,
            page_size=page_size,
        )
        return SearchResponse(
            mode=SearchMode.NAME,
            total=total,
            items=items,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}",
        )


@router.get("/by-tags", response_model=SearchResponse, summary="按标签搜索小说")
async def search_by_tags(
    tag_names: str = Query(..., description="标签名称列表，逗号分隔（如: 玄幻,重生,爽文）"),
    match_all: bool = Query(True, description="是否要求匹配所有标签"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    按标签搜索小说
    - 支持多标签组合搜索（按标签名称）
    - match_all=True 时要求匹配所有标签（AND），否则匹配任意标签（OR）
    """
    tag_name_list = [name.strip() for name in tag_names.split(",") if name.strip()]

    if not tag_name_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要提供一个标签名称",
        )

    try:
        items, total = await search_service.search_by_tags(
            db=db,
            tag_names=tag_name_list,
            match_all=match_all,
            page=page,
            page_size=page_size,
        )
        return SearchResponse(
            mode=SearchMode.TAG,
            total=total,
            items=items,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"搜索失败: {str(e)}",
        )
