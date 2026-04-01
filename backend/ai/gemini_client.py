"""Google Gemini API客户端"""
import asyncio
import logging
from typing import Optional

import httpx

from backend.ai.base_client import BaseAIClient

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiClient(BaseAIClient):
    """Google Gemini 客户端"""

    def __init__(self, api_url: str, api_key: Optional[str], model_identifier: str, max_tokens: int = 4096):
        super().__init__(api_url, api_key, model_identifier, max_tokens)
        if not self.api_url:
            self.api_url = DEFAULT_GEMINI_API_URL

    def _get_request_url(self) -> str:
        """构建 Gemini 请求 URL，API Key 放在 URL 参数里"""
        base = self.api_url.rstrip("/")
        return f"{base}/models/{self.model_identifier}:generateContent?key={self.api_key}"

    def _build_payload(self, prompt: str, max_tokens: Optional[int] = None) -> dict:
        """Gemini 请求体格式"""
        return {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens or self.max_tokens,
            },
        }

    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """调用 Gemini API 生成文本"""
        url = self._get_request_url()
        payload = self._build_payload(prompt, max_tokens)
        headers = {"Content-Type": "application/json"}
        last_exception = None

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()

                    # Gemini 返回格式: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    logger.info("Gemini API调用成功，模型: %s", self.model_identifier)
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
                    "Gemini API调用失败 (第%d次尝试): %s，%d秒后重试",
                    attempt + 1, error_detail, wait_time,
                )
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 400:
                    break
                if attempt < 2:
                    await asyncio.sleep(wait_time)

        raise RuntimeError(f"Gemini API调用失败，已重试3次: {last_exception}")
