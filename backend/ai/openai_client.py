"""OpenAI兼容API客户端 - 支持OpenAI及兼容接口"""
import asyncio
import logging
from typing import Optional

import httpx

from backend.ai.base_client import BaseAIClient

logger = logging.getLogger(__name__)


class OpenAIClient(BaseAIClient):
    """OpenAI兼容API客户端，适用于OpenAI及兼容格式的API"""

    def __init__(self, api_url: str, api_key: Optional[str], model_identifier: str, max_tokens: int = 4096):
        super().__init__(api_url, api_key, model_identifier, max_tokens)
        # 默认API地址
        if not self.api_url:
            self.api_url = "https://api.openai.com/v1/chat/completions"
        # 自动补全 /chat/completions 路径
        elif self.api_url.rstrip("/").endswith("/v1"):
            self.api_url = self.api_url.rstrip("/") + "/chat/completions"

    def _build_headers(self) -> dict:
        """构建请求头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_payload(self, prompt: str, max_tokens: Optional[int] = None) -> dict:
        """构建请求体"""
        return {
            "model": self.model_identifier,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or self.max_tokens,
        }

    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        调用OpenAI兼容API生成文本

        支持最多3次重试，使用指数退避策略
        """
        headers = self._build_headers()
        payload = self._build_payload(prompt, max_tokens)
        last_exception: Optional[Exception] = None

        # 最多重试3次，指数退避
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()

                    # 解析返回结果，提取生成的文本
                    text = data["choices"][0]["message"]["content"].strip()
                    logger.info("OpenAI API调用成功，模型: %s", self.model_identifier)
                    return text

            except (httpx.HTTPStatusError, httpx.RequestError, KeyError, IndexError) as exc:
                last_exception = exc
                wait_time = 2 ** attempt  # 1s, 2s, 4s 指数退避
                logger.warning(
                    "OpenAI API调用失败 (第%d次尝试): %s，%d秒后重试",
                    attempt + 1, str(exc), wait_time,
                )
                if attempt < 2:
                    await asyncio.sleep(wait_time)

        # 所有重试均失败
        raise RuntimeError(f"OpenAI API调用失败，已重试3次: {last_exception}")
