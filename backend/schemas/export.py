"""导出相关请求/响应模型"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ExportFormat(str, Enum):
    """导出格式"""
    TXT = "txt"
    DOCX = "docx"


class ExportRequest(BaseModel):
    """导出请求"""
    format: ExportFormat = Field(ExportFormat.TXT, description="导出格式")


class BatchExportRequest(BaseModel):
    """批量导出请求"""
    novel_ids: List[int] = Field(..., min_length=1, max_length=20, description="小说ID列表（最多20个）")
    format: ExportFormat = Field(ExportFormat.TXT, description="导出格式")


class ExportResponse(BaseModel):
    """导出响应"""
    file_name: str
    file_path: str
    format: ExportFormat
