"""总结相关请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SummaryRequest(BaseModel):
    """生成总结请求"""
    target_length: int = Field(100, ge=50, le=300, description="目标总结长度（字数）")
    model_id: Optional[int] = Field(None, description="指定AI模型ID，不指定则使用默认模型")


class SummaryUpdate(BaseModel):
    """编辑总结请求"""
    content: str = Field(..., min_length=1, description="修改后的总结内容")


class SummaryResponse(BaseModel):
    id: int
    novel_id: int
    content: str
    target_length: int
    actual_length: int
    model_used: Optional[str] = None
    is_chunk_summary: bool = False
    chunk_index: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChunkProgressResponse(BaseModel):
    """分段处理进度"""
    novel_id: int
    total_chunks: int
    completed_chunks: int
    status: str  # processing/merging/done/error
    progress_percent: float
