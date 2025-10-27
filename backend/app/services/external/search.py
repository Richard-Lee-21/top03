"""
搜索服务集成
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from app.core.config import settings
from app.core.exceptions import SearchAPIError, ValidationError

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务类 - 集成Serper API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        self.timeout = settings.SEARCH_TIMEOUT

    async def search_products(self, keyword: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索商品相关信息

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数量

        Returns:
            搜索结果列表
        """
        try:
            # 构建搜索查询，加入商品相关关键词
            search_query = f"best {keyword} reviews 2024 buy guide comparison"

            # 准备请求参数
            payload = {
                "q": search_query,
                "num": max_results,
                "hl": "zh-cn",
                "gl": "cn"
            }

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()

            # 解析搜索结果
            results = self._parse_search_results(data)

            logger.info(f"Found {len(results)} search results for keyword: {keyword}")
            return results

        except httpx.HTTPStatusError as e:
            logger.error(f"Search API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                raise SearchAPIError("搜索API密钥无效", service_name="Serper API")
            elif e.response.status_code == 429:
                raise SearchAPIError("搜索API调用频率超限，请稍后重试", service_name="Serper API")
            else:
                raise SearchAPIError(f"搜索API请求失败: {e.response.status_code}", service_name="Serper API")

        except httpx.TimeoutException:
            logger.error("Search API request timeout")
            raise SearchAPIError("搜索服务请求超时", service_name="Serper API")

        except httpx.RequestError as e:
            logger.error(f"Search API request error: {e}")
            raise SearchAPIError("搜索服务网络错误", service_name="Serper API")

        except Exception as e:
            logger.error(f"Unexpected error in search service: {e}")
            raise SearchAPIError("搜索服务异常", service_name="Serper API")

    def _parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析搜索结果数据"""
        results = []

        # 解析有机搜索结果
        if "organic" in data:
            for item in data["organic"]:
                result = {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "position": item.get("position", 0),
                    "favicon": item.get("favicon", ""),
                    "date": item.get("date", "")
                }
                results.append(result)

        # 解析知识图谱结果（如果有）
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            kg_result = {
                "title": kg.get("title", ""),
                "link": kg.get("descriptionLink", ""),
                "snippet": kg.get("description", ""),
                "position": 0,
                "favicon": "",
                "date": "",
                "type": "knowledge_graph"
            }
            results.insert(0, kg_result)

        return results

    async def search_with_fallback(self, keyword: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        带降级策略的搜索
        """
        try:
            return await self.search_products(keyword, max_results)
        except SearchAPIError as e:
            logger.warning(f"Primary search service failed: {e.message}")

            # 尝试备用搜索策略
            try:
                return await self._fallback_search(keyword, max_results)
            except Exception as fallback_error:
                logger.error(f"Fallback search also failed: {fallback_error}")
                raise SearchAPIError("所有搜索服务都不可用", service_name="Search Service")

    async def _fallback_search(self, keyword: str, max_results: int) -> List[Dict[str, Any]]:
        """
        备用搜索实现（这里可以实现备用搜索引擎或缓存搜索）
        """
        # 这里可以实现：
        # 1. 备用搜索引擎API
        # 2. 本地缓存搜索
        # 3. 基于历史数据的推荐

        logger.info(f"Using fallback search for keyword: {keyword}")

        # 简单的模拟搜索结果
        fallback_results = [
            {
                "title": f"Best {keyword} Products 2024",
                "link": "https://example.com/best-products",
                "snippet": f"Comprehensive guide to the best {keyword} available in 2024",
                "position": 1,
                "favicon": "",
                "date": "",
                "source": "fallback"
            }
        ]

        return fallback_results[:max_results]

    @staticmethod
    def validate_search_query(query: str) -> bool:
        """验证搜索查询"""
        if not query or len(query.strip()) == 0:
            return False

        if len(query) > 200:
            return False

        # 检查是否包含特殊字符（可根据需要扩展）
        forbidden_chars = ["<", ">", "|", "{", "}", "[", "]", "\\", "^", "`"]
        if any(char in query for char in forbidden_chars):
            return False

        return True

    def build_search_query(self, keyword: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """构建优化的搜索查询"""
        base_query = f"best {keyword} reviews 2024"

        if filters:
            if filters.get("price_range"):
                price_range = filters["price_range"]
                if price_range == "budget":
                    base_query += " budget cheap affordable"
                elif price_range == "premium":
                    base_query += " premium high-end luxury"

            if filters.get("brand"):
                base_query += f" {filters['brand']}"

            if filters.get("features"):
                features = " ".join(filters["features"])
                base_query += f" {features}"

        return base_query