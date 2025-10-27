"""
LLM服务集成 - 支持Claude和OpenAI
"""

import json
import httpx
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.exceptions import LLMAPIError, ValidationError

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """LLM提供商基类"""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = settings.LLM_TIMEOUT

    @abstractmethod
    async def analyze_search_results(
        self,
        keyword: str,
        search_results: List[Dict[str, Any]],
        system_prompt: str,
        user_prompt_template: str,
        tool_definition: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分析搜索结果并生成推荐"""
        pass


class ClaudeProvider(BaseLLMProvider):
    """Claude API提供商"""

    def __init__(self, api_key: str, model_name: str = "claude-3-haiku-20240307"):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def analyze_search_results(
        self,
        keyword: str,
        search_results: List[Dict[str, Any]],
        system_prompt: str,
        user_prompt_template: str,
        tool_definition: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """使用Claude分析搜索结果"""
        try:
            # 准备用户消息
            user_prompt = user_prompt_template.replace(
                "[USER_KEYWORD]", keyword
            ).replace(
                "[SEARCH_RESULTS]", json.dumps(search_results, indent=2, ensure_ascii=False)
            )

            # 准备请求
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            payload = {
                "model": self.model_name,
                "max_tokens": 4000,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "tools": [tool_definition],
                "tool_choice": {"type": "tool", "name": "report_top3_products"}
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                data = response.json()

            # 解析响应
            return self._parse_claude_response(data)

        except httpx.HTTPStatusError as e:
            logger.error(f"Claude API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                raise LLMAPIError("Claude API密钥无效", service_name="Claude API")
            elif e.response.status_code == 429:
                raise LLMAPIError("Claude API调用频率超限", service_name="Claude API")
            else:
                raise LLMAPIError(f"Claude API请求失败: {e.response.status_code}", service_name="Claude API")

        except httpx.TimeoutException:
            logger.error("Claude API request timeout")
            raise LLMAPIError("Claude服务请求超时", service_name="Claude API")

        except Exception as e:
            logger.error(f"Unexpected error in Claude service: {e}")
            raise LLMAPIError("Claude服务异常", service_name="Claude API")

    def _parse_claude_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析Claude API响应"""
        try:
            content = data.get("content", [])

            for item in content:
                if item.get("type") == "tool_use" and item.get("name") == "report_top3_products":
                    tool_input = item.get("input", {})
                    return tool_input.get("products", [])

            # 如果没有找到工具调用，尝试从文本中解析
            return self._fallback_parse_response(data)

        except Exception as e:
            logger.error(f"Failed to parse Claude response: {e}")
            raise LLMAPIError("Claude响应解析失败", service_name="Claude API")

    def _fallback_parse_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """备用解析方案"""
        # 这里可以实现更复杂的文本解析逻辑
        # 目前返回空列表，让调用方处理
        return []


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API提供商"""

    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo-preview"):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def analyze_search_results(
        self,
        keyword: str,
        search_results: List[Dict[str, Any]],
        system_prompt: str,
        user_prompt_template: str,
        tool_definition: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """使用OpenAI分析搜索结果"""
        try:
            # 准备用户消息
            user_prompt = user_prompt_template.replace(
                "[USER_KEYWORD]", keyword
            ).replace(
                "[SEARCH_RESULTS]", json.dumps(search_results, indent=2, ensure_ascii=False)
            )

            # 转换工具定义为OpenAI格式
            openai_tool = self._convert_tool_definition(tool_definition)

            # 准备请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "tools": [openai_tool],
                "tool_choice": {"type": "function", "function": {"name": "report_top3_products"}},
                "temperature": 0.3,
                "max_tokens": 4000
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

                data = response.json()

            # 解析响应
            return self._parse_openai_response(data)

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                raise LLMAPIError("OpenAI API密钥无效", service_name="OpenAI API")
            elif e.response.status_code == 429:
                raise LLMAPIError("OpenAI API调用频率超限", service_name="OpenAI API")
            else:
                raise LLMAPIError(f"OpenAI API请求失败: {e.response.status_code}", service_name="OpenAI API")

        except httpx.TimeoutException:
            logger.error("OpenAI API request timeout")
            raise LLMAPIError("OpenAI服务请求超时", service_name="OpenAI API")

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI service: {e}")
            raise LLMAPIError("OpenAI服务异常", service_name="OpenAI API")

    def _convert_tool_definition(self, tool_def: Dict[str, Any]) -> Dict[str, Any]:
        """转换工具定义为OpenAI格式"""
        return {
            "type": "function",
            "function": {
                "name": tool_def["name"],
                "description": tool_def["description"],
                "parameters": tool_def["input_schema"]
            }
        }

    def _parse_openai_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析OpenAI API响应"""
        try:
            choices = data.get("choices", [])
            if not choices:
                return []

            message = choices[0].get("message", {})
            tool_calls = message.get("tool_calls", [])

            for tool_call in tool_calls:
                if tool_call.get("function", {}).get("name") == "report_top3_products":
                    arguments = tool_call["function"]["arguments"]
                    tool_input = json.loads(arguments)
                    return tool_input.get("products", [])

            return []

        except Exception as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            raise LLMAPIError("OpenAI响应解析失败", service_name="OpenAI API")


class LLMService:
    """LLM服务管理类"""

    def __init__(self, provider: str, api_key: str, model_name: str):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model_name = model_name

        # 初始化具体的提供商
        if self.provider == "anthropic":
            self.client = ClaudeProvider(api_key, model_name)
        elif self.provider == "openai":
            self.client = OpenAIProvider(api_key, model_name)
        else:
            raise ValidationError(f"不支持的LLM提供商: {provider}")

    async def analyze_products(
        self,
        keyword: str,
        search_results: List[Dict[str, Any]],
        system_prompt: str,
        user_prompt_template: str,
        tool_definition: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分析商品并生成推荐"""
        try:
            # 验证输入
            if not keyword or not search_results:
                raise ValidationError("关键词和搜索结果不能为空")

            if len(search_results) == 0:
                raise ValidationError("搜索结果为空，无法进行分析")

            # 调用具体的LLM提供商
            results = await self.client.analyze_search_results(
                keyword=keyword,
                search_results=search_results,
                system_prompt=system_prompt,
                user_prompt_template=user_prompt_template,
                tool_definition=tool_definition
            )

            # 验证结果
            if not results or len(results) == 0:
                logger.warning("LLM returned empty results")
                return self._generate_fallback_results(keyword)

            # 确保返回3个结果
            if len(results) < 3:
                logger.warning(f"LLM returned only {len(results)} results, expected 3")
                # 可以在这里补充结果或使用降级策略

            logger.info(f"LLM analysis completed for keyword: {keyword}")
            return results[:3]  # 确保最多返回3个

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # 返回降级结果
            return self._generate_fallback_results(keyword)

    def _generate_fallback_results(self, keyword: str) -> List[Dict[str, Any]]:
        """生成降级结果"""
        logger.warning(f"Using fallback results for keyword: {keyword}")

        fallback_results = [
            {
                "rank": 1,
                "product_name": f"优质{keyword}产品",
                "description": "由于AI分析服务暂时不可用，这是一个基于搜索结果的简单推荐。建议您稍后重试获取更详细的分析。",
                "source_link": "https://example.com",
                "price": "价格待查",
                "rating": 4.0,
                "pros": ["基于搜索结果推荐"],
                "cons": ["AI分析服务暂时不可用"],
                "best_for": "需要快速参考的用户"
            }
        ]

        return fallback_results