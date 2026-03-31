"""
小说管理路由
提供小说上传、手动输入、列表查询、详情查看、删除等接口
"""

import os
import shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.dependencies import get_db, get_current_user
from backend.schemas.novel import (
    NovelCreate,
    NovelResponse,
    NovelListResponse,
    NovelDetail,
)
from backend.services import novel_service, file_parser, dedup_service

router = APIRouter(prefix="/novels", tags=["小说管理"])

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {".txt", ".pdf"}


@router.post("/upload", response_model=NovelResponse, status_code=status.HTTP_201_CREATED, summary="上传小说文件")
async def upload_novel(
    file: UploadFile = File(..., description="小说文件（TXT/PDF）"),
    title: Optional[str] = Form(None, description="小说标题，不填则使用文件名"),
    author: Optional[str] = Form(None, description="作者"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    上传小说文件（支持 TXT 和 PDF 格式）
    - 校验文件扩展名和大小
    - 计算文件哈希，检查是否重复上传
    - 解析文件提取文本内容
    - 创建小说记录
    """
    # 校验文件扩展名
    filename = file.filename or "unknown.txt"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式: {ext}，仅支持 .txt 和 .pdf",
        )

    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 保存上传文件到临时路径
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    try:
        # 读取文件内容并校验大小
        content = await file.read()
        file_size = len(content)
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制（最大 {settings.MAX_UPLOAD_SIZE_MB}MB）",
            )

        # 写入磁盘
        with open(file_path, "wb") as f:
            f.write(content)

        # 计算文件哈希值
        file_hash = dedup_service.compute_file_hash(file_path)

        # 检查是否重复上传
        existing = await dedup_service.check_duplicate(db, file_hash)
        if existing:
            # 清理临时文件
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"该文件已存在，对应小说: {existing.title}（ID: {existing.id}）",
            )

        # 解析文件内容
        cleaned_text, char_count = file_parser.parse_file(file_path, filename)

        # 使用文件名作为默认标题（去掉扩展名）
        if not title:
            title = os.path.splitext(filename)[0]

        # 创建小说记录
        novel = await novel_service.create_novel(
            db=db,
            title=title,
            author=author,
            file_path=file_path,
            file_hash=file_hash,
            file_size=file_size,
            char_count=char_count,
        )
        await db.commit()
        await db.refresh(novel)
        return novel

    except HTTPException:
        raise
    except Exception as e:
        # 出错时清理已保存的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传处理失败: {str(e)}",
        )


@router.post("/text", response_model=NovelResponse, status_code=status.HTTP_201_CREATED, summary="手动输入小说文本")
async def submit_novel_text(
    data: NovelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    手动输入小说文本
    - 计算文本哈希，检查是否重复
    - 将文本保存为文件
    - 创建小说记录
    """
    if not data.text_content or not data.text_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="小说文本内容不能为空",
        )

    try:
        text = data.text_content.strip()

        # 计算文本哈希
        text_hash = dedup_service.compute_text_hash(text)

        # 检查重复
        existing = await dedup_service.check_duplicate(db, text_hash)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"该文本已存在，对应小说: {existing.title}（ID: {existing.id}）",
            )

        # 保存文本到文件
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_name = f"{data.title}.txt"
        file_path = os.path.join(settings.UPLOAD_DIR, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        char_count = len(text)

        # 创建小说记录
        novel = await novel_service.create_novel(
            db=db,
            title=data.title,
            author=data.author,
            file_path=file_path,
            file_hash=text_hash,
            file_size=len(text.encode("utf-8")),
            char_count=char_count,
        )
        await db.commit()
        await db.refresh(novel)
        return novel

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文本提交处理失败: {str(e)}",
        )


@router.get("/", response_model=NovelListResponse, summary="获取小说列表")
async def list_novels(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态过滤（uploaded/processing/done/error）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    分页查询小说列表
    支持按状态过滤
    """
    try:
        novels, total = await novel_service.list_novels(
            db=db,
            page=page,
            page_size=page_size,
            status_filter=status,
        )
        return NovelListResponse(
            total=total,
            items=novels,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询小说列表失败: {str(e)}",
        )


@router.get("/{novel_id}", response_model=NovelDetail, summary="获取小说详情")
async def get_novel_detail(
    novel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    获取小说详情，包含摘要和标签信息
    """
    try:
        detail = await novel_service.get_novel_detail(db, novel_id)
        if not detail:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )

        novel = detail["novel"]
        return NovelDetail(
            id=novel.id,
            title=novel.title,
            author=novel.author,
            file_hash=novel.file_hash,
            file_size=novel.file_size,
            char_count=novel.char_count,
            status=novel.status,
            upload_time=novel.upload_time,
            updated_at=novel.updated_at,
            summaries=detail["summaries"],
            tags=detail["tags"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取小说详情失败: {str(e)}",
        )


@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除小说")
async def delete_novel(
    novel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    删除小说及其关联的摘要和标签数据
    """
    try:
        success = await novel_service.delete_novel(db, novel_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"小说不存在（ID: {novel_id}）",
            )
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除小说失败: {str(e)}",
        )
