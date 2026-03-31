"""
导出路由
提供单篇小说导出和批量导出接口，支持 TXT 和 DOCX 格式
"""

import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db, get_current_user
from backend.schemas.export import ExportRequest, BatchExportRequest
from backend.services import export_service, novel_service

router = APIRouter(prefix="/export", tags=["导出"])


@router.post("/{novel_id}", summary="导出单篇小说")
async def export_novel(
    novel_id: int,
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    导出单篇小说的总结和标签信息
    - 支持 TXT 和 DOCX 格式
    - 返回文件下载响应
    """
    try:
        # 校验小说是否存在
        novel = await novel_service.get_novel(db, novel_id)
        if not novel:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        # 调用导出服务
        result = await export_service.export_novel(
            db=db,
            novel_id=novel_id,
            export_format=request.format,
        )

        file_path = result["file_path"]
        file_name = result["file_name"]

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=500,
                detail="导出文件生成失败",
            )

        # 根据格式设置 Content-Type
        media_type = "text/plain; charset=utf-8"
        if request.format.value == "docx":
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type=media_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}",
        )


@router.post("/batch", summary="批量导出小说")
async def batch_export_novels(
    request: BatchExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    批量导出多篇小说的总结和标签信息
    - 最多支持 20 篇小说同时导出
    - 返回 ZIP 压缩包
    """
    try:
        # 调用批量导出服务
        result = await export_service.batch_export_novels(
            db=db,
            novel_ids=request.novel_ids,
            export_format=request.format,
        )

        file_path = result["file_path"]
        file_name = result["file_name"]

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=500,
                detail="导出文件生成失败",
            )

        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="application/zip",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量导出失败: {str(e)}",
        )
