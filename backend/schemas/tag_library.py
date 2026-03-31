"""传统标签库请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class TagLibraryCreate(BaseModel):
    """添加标签到标签库"""
    name: str = Field(..., max_length=100, description="标签名称")
    dimension: str = Field(..., description="标签维度")
    description: Optional[str] = Field(None, max_length=500, description="标签描述")
    sort_order: int = Field(0, description="排序序号")


class TagLibraryUpdate(BaseModel):
    """更新标签库条目"""
    name: Optional[str] = Field(None, max_length=100)
    dimension: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    sort_order: Optional[int] = None


class TagLibraryResponse(BaseModel):
    id: int
    name: str
    dimension: str
    description: Optional[str] = None
    sort_order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class TagLibraryListResponse(BaseModel):
    total: int
    items: List[TagLibraryResponse]


class TagLibraryBatchCreate(BaseModel):
    """批量添加标签"""
    tags: List[TagLibraryCreate]
