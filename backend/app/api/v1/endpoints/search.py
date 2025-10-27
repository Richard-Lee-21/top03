"""
搜索相关API端点
"""

import time
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ValidationError, ExternalAPIError
from app.core.redis import cache_service, cache
from app.schemas.search import SearchRequest, SearchResponse
from app.services.configuration import ConfigurationService
from app.services.external import SearchService, LLMService

logger = logging.getLogger(__name__)

router = APIRouter()


@cache("search:{keyword}", ttl=21600)  # 6小时缓存
@router.post("/", response_model=SearchResponse)
async def get_top_products(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    获取商品推荐
    """
    start_time = time.time()

    try:
        # 验证输入
        if not request.keyword or len(request.keyword.strip()) == 0:
            raise ValidationError("商品关键词不能为空")

        if len(request.keyword) > 200:
            raise ValidationError("商品关键词长度不能超过200个字符")

        keyword = request.keyword.strip()

        # 验证搜索查询
        if not SearchService.validate_search_query(keyword):
            raise ValidationError("搜索关键词包含无效字符")

        # 获取配置服务
        config_service = ConfigurationService(db)

        # 获取配置（带缓存）
        configs = await _get_cached_configs(config_service)

        # 检查API密钥是否配置
        serper_key = configs.get("SERPER_API_KEY")
        llm_key = configs.get("LLM_API_KEY")
        llm_provider = configs.get("LLM_PROVIDER", "anthropic")
        llm_model = configs.get("LLM_MODEL_NAME", "claude-3-haiku-20240307")

        if not serper_key or serper_key == "your-serper-api-key-here":
            raise ValidationError("搜索服务API密钥未配置，请联系管理员")

        if not llm_key or llm_key == "your-claude-or-openai-api-key-here":
            raise ValidationError("AI分析服务API密钥未配置，请联系管理员")

        # 获取Prompt配置
        system_prompt = configs.get("LLM_SYSTEM_PROMPT")
        user_prompt_template = configs.get("LLM_USER_PROMPT_TEMPLATE")
        tool_definition_str = configs.get("LLM_TOOL_DEFINITION")

        if not all([system_prompt, user_prompt_template, tool_definition_str]):
            logger.warning("Missing LLM configuration, using defaults")
            # 使用默认配置
            from app.core.seed_data import get_configuration_by_key
            default_configs = {
                "LLM_SYSTEM_PROMPT": get_configuration_by_key("LLM_SYSTEM_PROMPT")["value"],
                "LLM_USER_PROMPT_TEMPLATE": get_configuration_by_key("LLM_USER_PROMPT_TEMPLATE")["value"],
                "LLM_TOOL_DEFINITION": get_configuration_by_key("LLM_TOOL_DEFINITION")["value"]
            }
            system_prompt = system_prompt or default_configs["LLM_SYSTEM_PROMPT"]
            user_prompt_template = user_prompt_template or default_configs["LLM_USER_PROMPT_TEMPLATE"]
            tool_definition_str = tool_definition_str or default_configs["LLM_TOOL_DEFINITION"]

        # 解析工具定义
        try:
            tool_definition = json.loads(tool_definition_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool definition: {e}")
            raise ValidationError("系统配置错误，工具定义格式无效")

        # 执行搜索和AI分析
        products = await _search_and_analyze(
            keyword=keyword,
            serper_key=serper_key,
            llm_key=llm_key,
            llm_provider=llm_provider,
            llm_model=llm_model,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            tool_definition=tool_definition
        )

        search_time = time.time() - start_time

        response = SearchResponse(
            products=products,
            total_results=len(products),
            search_time=round(search_time, 2),
            cached=False  # 缓存装饰器会自动处理
        )

        logger.info(f"Search completed for keyword '{keyword}' in {search_time:.2f}s")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "message": e.message,
            "code": e.code
        })
    except ExternalAPIError as e:
        logger.error(f"External API error: {e.message}")
        raise HTTPException(status_code=502, detail={
            "status": "error",
            "message": e.message,
            "code": e.code
        })
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "服务器内部错误，请稍后重试",
            "code": "INTERNAL_SERVER_ERROR"
        })


async def _get_cached_configs(config_service: ConfigurationService) -> Dict[str, str]:
    """获取缓存的配置"""
    cache_key = "app_configs"
    cached_configs = await cache_service.get(cache_key)

    if cached_configs:
        return cached_configs

    # 从数据库获取配置
    configs = await config_service.get_configuration_dict()

    # 缓存1分钟
    await cache_service.set(cache_key, configs, ttl=60)

    return configs


async def _search_and_analyze(
    keyword: str,
    serper_key: str,
    llm_key: str,
    llm_provider: str,
    llm_model: str,
    system_prompt: str,
    user_prompt_template: str,
    tool_definition: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """执行搜索和AI分析"""
    try:
        # 第一步：搜索
        search_service = SearchService(serper_key)
        search_results = await search_service.search_with_fallback(keyword, max_results=10)

        if not search_results:
            logger.warning(f"No search results found for keyword: {keyword}")
            return _generate_empty_results(keyword)

        # 第二步：AI分析
        llm_service = LLMService(llm_provider, llm_key, llm_model)
        analyzed_products = await llm_service.analyze_products(
            keyword=keyword,
            search_results=search_results,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            tool_definition=tool_definition
        )

        return analyzed_products

    except Exception as e:
        logger.error(f"Error in search and analyze: {e}")
        return _generate_fallback_results(keyword)


def _generate_empty_results(keyword: str) -> List[Dict[str, Any]]:
    """生成空结果"""
    return [{
        "rank": 1,
        "product_name": f"未找到{keyword}相关产品",
        "description": "很抱歉，没有找到相关的商品推荐。请尝试使用其他关键词或稍后重试。",
        "source_link": "https://example.com",
        "price": "暂无",
        "rating": 0.0,
        "pros": [],
        "cons": ["未找到相关商品"],
        "best_for": "建议尝试其他搜索词"
    }]


def _generate_fallback_results(keyword: str) -> List[Dict[str, Any]]:
    """生成降级结果"""
    logger.warning(f"Using fallback results for keyword: {keyword}")

    return [{
        "rank": 1,
        "product_name": f"{keyword}产品推荐",
        "description": "由于服务暂时不可用，建议您稍后重试获取更准确的商品推荐。您可以尝试在各大电商平台搜索相关商品。",
        "source_link": "https://example.com",
        "price": "价格待查",
        "rating": 3.5,
        "pros": ["建议多平台比较"],
        "cons": ["服务暂时不可用"],
        "best_for": "需要自行研究的用户"
    }]