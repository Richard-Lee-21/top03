"""
配置相关的Pydantic模型
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConfigurationBase(BaseModel):
    """配置基础模型"""
    key: str = Field(..., min_length=1, max_length=100, description="配置键")
    value: str = Field(..., description="配置值")
    group: str = Field(..., regex="^(api|prompt|ui|cache)$", description="配置组")


class ConfigurationCreate(ConfigurationBase):
    """创建配置模型"""
    pass


class ConfigurationUpdate(BaseModel):
    """更新配置模型"""
    value: str = Field(..., description="配置值")


class Configuration(ConfigurationBase):
    """配置完整模型"""
    id: int = Field(..., description="配置ID")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "key": "LLM_SYSTEM_PROMPT",
                "value": "你是一个世界级的产品分析师...",
                "group": "prompt",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }


class ConfigurationBatchUpdate(BaseModel):
    """批量更新配置模型"""
    settings: list[dict[str, str]] = Field(..., description="配置项列表")

    class Config:
        schema_extra = {
            "example": {
                "settings": [
                    {
                        "key": "LLM_MODEL_NAME",
                        "value": "claude-3-opus-20240229"
                    },
                    {
                        "key": "LLM_SYSTEM_PROMPT",
                        "value": "你是一个专业的产品分析师..."
                    }
                ]
            }
        }