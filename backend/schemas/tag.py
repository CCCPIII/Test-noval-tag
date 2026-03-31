"""标签相关请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TagDimension(str, Enum):
    """标签维度枚举"""
    GENRE = "genre"          # 题材标签
    STYLE = "style"          # 风格标签
    ELEMENT = "element"      # 核心元素标签
    CHARACTER = "character"  # 人物类型标签
    EXCLUSIVE = "exclusive"  # 专属标签


class TagCreate(BaseModel):
    """创建标签"""
    name: str = Field(..., max_length=100, description="标签名称")
    dimension: TagDimension = Field(..., description="标签维度")


class TagResponse(BaseModel):
    id: int
    name: str
    dimension: str
    is_custom: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class TagAssign(BaseModel):
    """为小说分配标签"""
    tag_id: int
    is_manual: bool = True
    is_controversial: bool = False
    controversy_note: Optional[str] = Field(None, max_length=200, description="争议标签解释（50字以内）")


class TagBatchAssign(BaseModel):
    """批量为小说分配标签"""
    tags: List[TagAssign]


class TagGenerateRequest(BaseModel):
    """AI生成标签请求"""
    model_config = {"protected_namespaces": ()}
    model_id: Optional[int] = Field(None, description="指定AI模型ID")


class TagGenerateResponse(BaseModel):
    """AI生成标签响应"""
    generated_tags: List[TagResponse]
    exclusive_tags: List[TagResponse]  # 专属标签（1-2个）
