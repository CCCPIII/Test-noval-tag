"""AI客户端工厂 - 根据模型配置创建对应客户端实例"""
from typing import Optional
from backend.ai.base_client import BaseAIClient
from backend.ai.openai_client import OpenAIClient
from backend.ai.zhipu_client import ZhipuClient
from backend.ai.local_model_client import LocalModelClient


# 提供商到客户端类的映射
_CLIENT_MAP = {
    "openai": OpenAIClient,
    "zhipu": ZhipuClient,
    "local": LocalModelClient,
    "custom": OpenAIClient,  # 自定义模型默认使用OpenAI兼容格式
}


def create_ai_client(
    provider: str,
    api_url: str,
    api_key: Optional[str],
    model_identifier: str,
    max_tokens: int = 4096
) -> BaseAIClient:
    """根据提供商类型创建对应的AI客户端"""
    client_cls = _CLIENT_MAP.get(provider)
    if not client_cls:
        raise ValueError(f"不支持的模型提供商: {provider}，支持的类型: {list(_CLIENT_MAP.keys())}")
    return client_cls(
        api_url=api_url,
        api_key=api_key,
        model_identifier=model_identifier,
        max_tokens=max_tokens
    )
