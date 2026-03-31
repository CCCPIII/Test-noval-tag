"""本地模型客户端 - 支持Ollama等本地部署的模型服务"""
import asyncio
import logging
from typing import Optional

import httpx

from backend.ai.base_client import BaseAIClient

logger = logging.getLogger(__name__)

# Ollama默认API地址
DEFAULT_LOCAL_API_URL = "http://localhost:11434/api/generate"


class LocalModelClient(BaseAIClient):
    """本地模型客户端，适用于Ollama等本地模型服务"""

    def __init__(self, api_url: str, api_key: Optional[str], model_identifier: str, max_tokens: int = 4096):
        super().__init__(api_url, api_key, model_identifier, max_tokens)
        # 如果未指定API地址，使用Ollama默认地址
        if not self.api_url:
            self.api_url = DEFAULT_LOCAL_API_URL

    def _build_payload(self, prompt: str, max_tokens: Optional[int] = None) -> dict:
        """构建本地模型请求体（Ollama格式）"""
        payload = {
            "model": self.model_identifier,
            "prompt": prompt,
            "stream": False,  # 禁用流式输出，直接返回完整结果
        }
        # 通过options设置最大生成token数
        effective_max_tokens = max_tokens or self.max_tokens
        if effective_max_tokens:
            payload["options"] = {"num_predict": effective_max_tokens}
        return payload

    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        调用本地模型服务生成文本

        支持最多3次重试，使用指数退避策略
        """
        payload = self._build_payload(prompt, max_tokens)
        headers = {"Content-Type": "application/json"}
        last_exception: Optional[Exception] = None

        # 最多重试3次，指数退避
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()

                    # 解析Ollama返回结果，提取生成的文本
                    text = data.get("response", "").strip()
                    if not text:
                        raise ValueError("本地模型返回结果为空")
                    logger.info("本地模型调用成功，模型: %s", self.model_identifier)
                    return text

            except (httpx.HTTPStatusError, httpx.RequestError, KeyError, ValueError) as exc:
                last_exception = exc
                wait_time = 2 ** attempt  # 1s, 2s, 4s 指数退避
                logger.warning(
                    "本地模型调用失败 (第%d次尝试): %s，%d秒后重试",
                    attempt + 1, str(exc), wait_time,
                )
                if attempt < 2:
                    await asyncio.sleep(wait_time)

        # 所有重试均失败
        raise RuntimeError(f"本地模型调用失败，已重试3次: {last_exception}")
