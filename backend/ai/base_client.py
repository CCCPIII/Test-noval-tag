"""AI模型客户端基类"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseAIClient(ABC):
    """AI模型客户端抽象基类，所有模型客户端需继承此类"""

    def __init__(self, api_url: str, api_key: Optional[str], model_identifier: str, max_tokens: int = 4096):
        self.api_url = api_url
        self.api_key = api_key
        self.model_identifier = model_identifier
        self.max_tokens = max_tokens

    @abstractmethod
    async def generate_text(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """调用AI模型生成文本"""
        pass

    async def generate_summary(self, text: str, target_length: int, prompt_template: str) -> str:
        """生成小说总结"""
        prompt = prompt_template.format(text=text, length=target_length)
        return await self.generate_text(prompt, max_tokens=target_length * 2)

    async def generate_tags(self, text: str, dimension: str, tag_library_ref: str, prompt_template: str) -> list:
        """生成标签，返回标签名称列表"""
        prompt = prompt_template.format(text=text, dimension=dimension, tag_library=tag_library_ref)
        result = await self.generate_text(prompt, max_tokens=500)
        # 解析返回的标签列表（逗号分隔）
        tags = [t.strip() for t in result.split(",") if t.strip()]
        return tags
