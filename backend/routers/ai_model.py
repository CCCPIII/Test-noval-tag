"""
AI 模型管理路由
提供 AI 模型配置的增删改查、连接测试等接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db, get_current_user
from backend.schemas.ai_model import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelListResponse,
    AIModelTestRequest,
    AIModelTestResponse,
)
from backend.services import ai_model_service

router = APIRouter(prefix="/ai-models", tags=["AI模型管理"])


@router.get("/", response_model=AIModelListResponse, summary="获取 AI 模型列表")
async def list_models(
    active_only: bool = Query(False, description="是否只返回启用的模型"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    获取所有 AI 模型配置列表
    支持只返回已启用的模型
    """
    try:
        items, total = await ai_model_service.list_models(
            db=db,
            active_only=active_only,
        )
        return AIModelListResponse(total=total, items=items)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询模型列表失败: {str(e)}",
        )


@router.get("/{model_id}", response_model=AIModelResponse, summary="获取模型详情")
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    获取指定 AI 模型的详细配置
    """
    try:
        model = await ai_model_service.get_model(db, model_id)
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"AI 模型不存在（ID: {model_id}）",
            )
        return model

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取模型详情失败: {str(e)}",
        )


@router.post("/", response_model=AIModelResponse, status_code=status.HTTP_201_CREATED, summary="创建模型配置")
async def create_model(
    data: AIModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    创建新的 AI 模型配置
    API 密钥将在存储时加密处理
    """
    try:
        model = await ai_model_service.create_model(db, data)
        await db.commit()
        await db.refresh(model)
        return model

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建模型失败: {str(e)}",
        )


@router.put("/{model_id}", response_model=AIModelResponse, summary="更新模型配置")
async def update_model(
    model_id: int,
    data: AIModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    更新指定 AI 模型的配置信息
    """
    try:
        model = await ai_model_service.update_model(db, model_id, data)
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"AI 模型不存在（ID: {model_id}）",
            )
        await db.commit()
        await db.refresh(model)
        return model

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新模型失败: {str(e)}",
        )


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除模型配置")
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    删除指定 AI 模型配置
    """
    try:
        success = await ai_model_service.delete_model(db, model_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"AI 模型不存在（ID: {model_id}）",
            )
        await db.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除模型失败: {str(e)}",
        )


@router.post("/{model_id}/test", response_model=AIModelTestResponse, summary="测试模型连接")
async def test_model(
    model_id: int,
    request: AIModelTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    测试 AI 模型的 API 连接是否正常
    - 发送测试提示词
    - 返回响应结果和响应时间
    """
    try:
        # 校验模型是否存在
        model = await ai_model_service.get_model(db, model_id)
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"AI 模型不存在（ID: {model_id}）",
            )

        # 执行连接测试
        result = await ai_model_service.test_connection(
            db=db,
            model_id=model_id,
            test_prompt=request.test_prompt,
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        # 连接测试失败不应返回 500，而是返回测试失败结果
        return AIModelTestResponse(
            success=False,
            error_message=str(e),
        )
