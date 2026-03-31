"""
AI 模型管理服务
管理 AI 模型配置的增删改查，包括 API Key 加密存储和连接测试
"""

import time
import logging
from typing import Optional
from cryptography.fernet import Fernet
import base64

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.ai_model import AIModel
from backend.schemas.ai_model import AIModelCreate, AIModelUpdate
from backend.core.config import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """
    获取 Fernet 加密器实例
    使用配置中的 ENCRYPTION_KEY 生成密钥
    """
    # 将 32 字节十六进制密钥转为 base64 编码（Fernet 要求 32 字节 URL-safe base64）
    key_bytes = settings.ENCRYPTION_KEY.encode("utf-8")[:32]
    key_b64 = base64.urlsafe_b64encode(key_bytes)
    return Fernet(key_b64)


def _encrypt_api_key(api_key: str) -> str:
    """加密 API Key"""
    fernet = _get_fernet()
    return fernet.encrypt(api_key.encode("utf-8")).decode("utf-8")


def _decrypt_api_key(encrypted_key: str) -> str:
    """解密 API Key"""
    fernet = _get_fernet()
    return fernet.decrypt(encrypted_key.encode("utf-8")).decode("utf-8")


async def create_model(db: AsyncSession, data: AIModelCreate) -> AIModel:
    """
    创建 AI 模型配置
    API Key 会被加密后存储
    """
    model = AIModel(
        name=data.name,
        provider=data.provider,
        api_url=data.api_url,
        model_identifier=data.model_identifier,
        max_tokens=data.max_tokens,
        description=data.description,
        supported_max_chars=data.supported_max_chars,
        avg_speed=data.avg_speed,
        accuracy_note=data.accuracy_note,
        is_active=True,
    )

    # 加密存储 API Key
    if data.api_key:
        model.api_key_encrypted = _encrypt_api_key(data.api_key)

    db.add(model)
    await db.flush()
    await db.refresh(model)
    return model


async def update_model(
    db: AsyncSession,
    model_id: int,
    data: AIModelUpdate,
) -> Optional[AIModel]:
    """
    更新 AI 模型配置
    仅更新传入的非 None 字段；如果更新了 API Key 则重新加密
    """
    stmt = select(AIModel).where(AIModel.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    if not model:
        return None

    # 逐字段更新
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "api_key" and value is not None:
            # API Key 需要加密后存储
            model.api_key_encrypted = _encrypt_api_key(value)
        elif field != "api_key" and value is not None:
            setattr(model, field, value)

    await db.flush()
    await db.refresh(model)
    return model


async def delete_model(db: AsyncSession, model_id: int) -> bool:
    """
    删除 AI 模型配置
    """
    stmt = select(AIModel).where(AIModel.id == model_id)
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    if not model:
        return False

    await db.delete(model)
    await db.flush()
    return True


async def list_models(db: AsyncSession, active_only: bool = False) -> list:
    """
    查询 AI 模型列表
    可选择仅返回启用状态的模型
    """
    stmt = select(AIModel)
    if active_only:
        stmt = stmt.where(AIModel.is_active == True)
    stmt = stmt.order_by(AIModel.created_at.desc())

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_model(db: AsyncSession, model_id: int) -> Optional[AIModel]:
    """
    根据 ID 获取单个 AI 模型配置
    """
    stmt = select(AIModel).where(AIModel.id == model_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_default_model(db: AsyncSession) -> Optional[AIModel]:
    """
    获取默认 AI 模型（第一个启用的模型）
    按创建时间升序，返回最早创建的活跃模型
    """
    stmt = (
        select(AIModel)
        .where(AIModel.is_active == True)
        .order_by(AIModel.created_at.asc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def test_model_connection(
    db: AsyncSession,
    model_id: int,
    test_prompt: str = "你好，请简单回复。",
) -> dict:
    """
    测试 AI 模型的连接是否正常

    发送一个简单的测试请求，记录响应时间和结果

    Returns:
        {
            "success": bool,
            "response_text": str or None,
            "error_message": str or None,
            "response_time_ms": float or None,
        }
    """
    model = await get_model(db, model_id)
    if not model:
        return {
            "success": False,
            "response_text": None,
            "error_message": "模型不存在",
            "response_time_ms": None,
        }

    start_time = time.time()

    try:
        # TODO: 根据 model.provider 调用对应的 AI 接口进行测试
        # 目前返回占位响应
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "success": True,
            "response_text": f"[占位响应] 模型 {model.name} 连接测试成功（待接入真实 AI 接口）",
            "error_message": None,
            "response_time_ms": round(elapsed_ms, 2),
        }
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        logger.error(f"模型连接测试失败: {model.name}, 错误: {e}")
        return {
            "success": False,
            "response_text": None,
            "error_message": str(e),
            "response_time_ms": round(elapsed_ms, 2),
        }
