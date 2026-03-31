"""搜索相关请求/响应模型"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SearchMode(str, Enum):
    """搜索模式"""
    NAME = "name"    # 名称搜索
    TAG = "tag"      # 标签搜索


class SearchByNameRequest(BaseModel):
    """名称搜索请求"""
    keyword: str = Field(..., min_length=1, description="搜索关键词")
    exact_match: bool = Field(False, description="是否精准匹配")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SearchByTagRequest(BaseModel):
    """标签搜索请求"""
    tag_ids: List[int] = Field(..., min_length=1, description="标签ID列表")
    match_all: bool = Field(True, description="是否要求匹配所有标签")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SearchResultItem(BaseModel):
    """搜索结果项"""
    novel_id: int
    title: str
    author: Optional[str] = None
    char_count: int = 0
    status: str
    summary_preview: Optional[str] = None  # 总结预览（前100字）
    tags: List[str] = []  # 标签名称列表
    match_score: Optional[float] = None  # 匹配度

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    """搜索结果响应"""
    mode: SearchMode
    total: int
    items: List[SearchResultItem]
    page: int
    page_size: int
