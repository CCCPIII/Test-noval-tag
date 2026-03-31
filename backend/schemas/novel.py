"""小说相关请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.schemas.summary import SummaryResponse


class NovelBase(BaseModel):
    title: str = Field(..., max_length=500, description="小说名称")
    author: Optional[str] = Field(None, max_length=200, description="作者")


class NovelCreate(NovelBase):
    """手动输入小说文本时使用"""
    text_content: Optional[str] = Field(None, description="手动输入的小说文本")


class NovelResponse(NovelBase):
    id: int
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    char_count: int = 0
    status: str = "uploaded"
    upload_time: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NovelListResponse(BaseModel):
    """小说列表响应"""
    total: int
    items: List[NovelResponse]
    page: int
    page_size: int


class NovelTagResponse(BaseModel):
    """小说关联的标签"""
    tag_id: int
    tag_name: str
    dimension: str
    confidence: Optional[float] = None
    is_manual: bool = False
    is_controversial: bool = False
    controversy_note: Optional[str] = None

    model_config = {"from_attributes": True}


class NovelDetail(NovelResponse):
    """小说详情，包含总结和标签"""
    summaries: List["SummaryResponse"] = []
    tags: List["NovelTagResponse"] = []


# Deferred import and model rebuild to resolve forward reference
from backend.schemas.summary import SummaryResponse  # noqa: E402
NovelDetail.model_rebuild()
