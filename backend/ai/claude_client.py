"""Anthropic Claude API客户端"""
import asyncio
import logging
from typing import Optional

import httpx

from backend.ai.base_client import BaseAIClient

logger = logging.getLogger(__name__)

DEFAULT_CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


class ClaudeClient(BaseAIClient):
    """Anthropic Claude 客户端，适用于 Claude 系列模型"""

    def __init__(self, api_url: str, api_key: Optional[str], model_identifier: str, max_tokens: int = 4096):
        super().__init__(api_url, api_key, model_identifier, max_tokens)
        if not self.api_url:
            self.api_url = DEFAULT_CLAUDE_API_URL
        elif self.api_url.rstrip("/").endswith("/v1"):
            self.api_url = self.api_url.rstrip("/") + "/messages"

    def _build_headers(self) -> dict:
        """Claude 使用 x-api-key 头传递密钥"""
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _build_payload(self, prompt: str, max_tokens: Optional[int] = None) -> dict:
        """Claude API 请求体格式与 OpenAI 不同"""
        return {
            "model": self.model_identifier,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or self.max_tokens,
        }

    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """调用 Claude API 生成文本"""
        headers = self._build_headers()
        payload = self._build_payload(prompt, max_tokens)
        last_exception = None

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

                    # Claude 返回格式: {"content": [{"type": "text", "text": "..."}]}
                    text = data["content"][0]["text"].strip()
                    logger.info("Claude API调用成功，模型: %s", self.model_identifier)
                    return text

            except (httpx.HTTPStatusError, httpx.RequestError, KeyError, IndexError) as exc:
                error_detail = str(exc)
                if isinstance(exc, httpx.HTTPStatusError):
                    try:
                        error_body = exc.response.json()
                        error_detail = error_body.get("error", {}).get("message", str(exc))
                    except Exception:
                        error_detail = exc.response.text or str(exc)
                last_exception = error_detail
                wait_time = 2 ** attempt
                logger.warning(
                    "Claude API调用失败 (第%d次尝试): %s，%d秒后重试",
                    attempt + 1, error_detail, wait_time,
                )
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 400:
                    break
                if attempt < 2:
                    await asyncio.sleep(wait_time)

        raise RuntimeError(f"Claude API调用失败，已重试3次: {last_exception}")
