"""AI模型API管理请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class AIModelCreate(BaseModel):
    """创建AI模型配置"""
    name: str = Field(..., max_length=100, description="模型名称")
    provider: str = Field(..., description="提供商(openai/zhipu/local/custom)")
    api_url: str = Field(..., max_length=500, description="API接口地址")
    api_key: Optional[str] = Field(None, description="API密钥（存储时加密）")
    model_identifier: str = Field(..., max_length=200, description="模型标识符")
    max_tokens: int = Field(4096, description="最大token数")
    description: Optional[str] = Field(None, max_length=1000, description="模型描述")
    supported_max_chars: Optional[int] = Field(None, description="支持的最大小说字数")
    avg_speed: Optional[str] = Field(None, max_length=50, description="平均速度")
    accuracy_note: Optional[str] = Field(None, max_length=200, description="准确率说明")


class AIModelUpdate(BaseModel):
    """更新AI模型配置"""
    name: Optional[str] = Field(None, max_length=100)
    provider: Optional[str] = None
    api_url: Optional[str] = Field(None, max_length=500)
    api_key: Optional[str] = None
    model_identifier: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    max_tokens: Optional[int] = None
    description: Optional[str] = Field(None, max_length=1000)
    supported_max_chars: Optional[int] = None
    avg_speed: Optional[str] = Field(None, max_length=50)
    accuracy_note: Optional[str] = Field(None, max_length=200)


class AIModelResponse(BaseModel):
    id: int
    name: str
    provider: str
    api_url: str
    model_identifier: str
    is_active: bool = True
    max_tokens: int
    description: Optional[str] = None
    supported_max_chars: Optional[int] = None
    avg_speed: Optional[str] = None
    accuracy_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AIModelListResponse(BaseModel):
    total: int
    items: List[AIModelResponse]


class AIModelTestRequest(BaseModel):
    """测试模型连接"""
    test_prompt: str = Field("你好，请简单回复。", description="测试用的提示词")


class AIModelTestResponse(BaseModel):
    success: bool
    response_text: Optional[str] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
