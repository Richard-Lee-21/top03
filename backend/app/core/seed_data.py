"""
种子数据配置
"""

from typing import List, Dict, Any
from app.models.configuration import Configuration


# 默认配置数据
DEFAULT_CONFIGURATIONS: List[Dict[str, Any]] = [
    # API配置组
    {
        "key": "SERPER_API_KEY",
        "value": "your-serper-api-key-here",
        "group": "api"
    },
    {
        "key": "LLM_API_KEY",
        "value": "your-claude-or-openai-api-key-here",
        "group": "api"
    },
    {
        "key": "LLM_PROVIDER",
        "value": "anthropic",
        "group": "api"
    },
    {
        "key": "LLM_MODEL_NAME",
        "value": "claude-3-haiku-20240307",
        "group": "api"
    },
    {
        "key": "SEARCH_TIMEOUT",
        "value": "30",
        "group": "api"
    },
    {
        "key": "LLM_TIMEOUT",
        "value": "60",
        "group": "api"
    },
    {
        "key": "MAX_RETRIES",
        "value": "3",
        "group": "api"
    },
    {
        "key": "MAX_SEARCH_RESULTS",
        "value": "10",
        "group": "api"
    },
    {
        "key": "TOP_PRODUCTS_COUNT",
        "value": "3",
        "group": "api"
    },

    # Prompt配置组
    {
        "key": "LLM_SYSTEM_PROMPT",
        "value": """你是一个世界级的产品分析师和市场调研专家。你的任务是分析给定的实时网络搜索结果，以找出关于特定商品的全网最佳推荐。

你需要基于以下的搜索结果（包括网页标题、摘要和链接），为用户寻找的商品综合判断出 Top 3 推荐。

分析标准：
1. 产品质量和性能 - 基于专业评测和用户反馈
2. 性价比 - 价格与功能的平衡
3. 品牌信誉和售后服务
4. 用户评价和满意度
5. 创新性和技术优势

对于每个推荐产品，请提供：
- 产品名称（完整准确）
- 推荐理由（详细说明为什么推荐该产品）
- 主要优点（3-4个关键优势）
- 潜在缺点或注意事项（1-2个）
- 适合人群（该产品最适合什么样的用户）
- 权威来源链接（专业评测或主要零售商链接）

请确保推荐客观、公正，基于真实的搜索结果数据。""",
        "group": "prompt"
    },
    {
        "key": "LLM_USER_PROMPT_TEMPLATE",
        "value": """请基于以下搜索结果，为商品 "[USER_KEYWORD]" 找出 Top 3 最佳推荐：

搜索结果：
[SEARCH_RESULTS]

请按照要求分析并推荐最优质的3款商品，确保推荐理由充分、客观。""",
        "group": "prompt"
    },
    {
        "key": "LLM_TOOL_DEFINITION",
        "value": """{
  "name": "report_top3_products",
  "description": "分析搜索结果并报告Top3商品推荐",
  "input_schema": {
    "type": "object",
    "properties": {
      "products": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "rank": {"type": "integer", "minimum": 1, "maximum": 3},
            "product_name": {"type": "string"},
            "description": {"type": "string"},
            "source_link": {"type": "string"},
            "price": {"type": "string"},
            "rating": {"type": "number", "minimum": 0, "maximum": 5},
            "pros": {
              "type": "array",
              "items": {"type": "string"}
            },
            "cons": {
              "type": "array",
              "items": {"type": "string"}
            },
            "best_for": {"type": "string"}
          },
          "required": ["rank", "product_name", "description", "source_link"]
        },
        "minItems": 3,
        "maxItems": 3
      }
    },
    "required": ["products"]
  }
}""",
        "group": "prompt"
    },

    # UI配置组
    {
        "key": "SITE_TITLE",
        "value": "Top3-Hunter - 智能商品推荐引擎",
        "group": "ui"
    },
    {
        "key": "SITE_DESCRIPTION",
        "value": "基于实时网络搜索和AI分析的商品推荐系统，为您推荐全网最优质的商品",
        "group": "ui"
    },
    {
        "key": "CONTACT_EMAIL",
        "value": "support@top3hunter.com",
        "group": "ui"
    },
    {
        "key": "ENABLE_RATINGS",
        "value": "true",
        "group": "ui"
    },
    {
        "key": "ENABLE_PRICES",
        "value": "true",
        "group": "ui"
    },
    {
        "key": "THEME_COLOR",
        "value": "#3b82f6",
        "group": "ui"
    },

    # 缓存配置组
    {
        "key": "CACHE_TTL_QUERY",
        "value": "21600",
        "group": "cache"
    },
    {
        "key": "CACHE_TTL_CONFIG",
        "value": "60",
        "group": "cache"
    },
    {
        "key": "CACHE_PREFIX",
        "value": "top3_hunter",
        "group": "cache"
    },
    {
        "key": "ENABLE_CACHE",
        "value": "true",
        "group": "cache"
    },
    {
        "key": "CACHE_ENABLED_SEARCH",
        "value": "true",
        "group": "cache"
    },
    {
        "key": "CACHE_ENABLED_CONFIG",
        "value": "true",
        "group": "cache"
    },
    {
        "key": "RATE_LIMIT_PER_MINUTE",
        "value": "30",
        "group": "cache"
    }
]


def get_seed_configurations() -> List[Configuration]:
    """获取种子配置数据列表"""
    configurations = []
    for config_data in DEFAULT_CONFIGURATIONS:
        config = Configuration(
            key=config_data["key"],
            value=config_data["value"],
            group=config_data["group"]
        )
        configurations.append(config)
    return configurations


def get_configuration_by_key(key: str) -> Dict[str, Any]:
    """根据键获取配置项"""
    for config in DEFAULT_CONFIGURATIONS:
        if config["key"] == key:
            return config
    return None


def get_configurations_by_group(group: str) -> List[Dict[str, Any]]:
    """根据组获取配置项列表"""
    return [config for config in DEFAULT_CONFIGURATIONS if config["group"] == group]


# 配置组描述
CONFIG_GROUP_DESCRIPTIONS = {
    "api": "API配置 - 外部服务接口设置",
    "prompt": "提示词配置 - AI分析和响应模板",
    "ui": "界面配置 - 前端显示和用户体验设置",
    "cache": "缓存配置 - 性能优化和限流设置"
}


# 必需的配置键
REQUIRED_CONFIG_KEYS = [
    "SERPER_API_KEY",
    "LLM_API_KEY",
    "LLM_PROVIDER",
    "LLM_MODEL_NAME",
    "LLM_SYSTEM_PROMPT",
    "LLM_USER_PROMPT_TEMPLATE",
    "LLM_TOOL_DEFINITION"
]


def validate_required_configurations(configurations: List[Configuration]) -> List[str]:
    """验证必需的配置项是否存在"""
    existing_keys = {config.key for config in configurations}
    missing_keys = set(REQUIRED_CONFIG_KEYS) - existing_keys
    return list(missing_keys)


# 配置验证规则
CONFIG_VALIDATION_RULES = {
    "LLM_PROVIDER": {"values": ["anthropic", "openai"], "required": True},
    "SEARCH_TIMEOUT": {"type": "int", "min": 5, "max": 120, "required": True},
    "LLM_TIMEOUT": {"type": "int", "min": 10, "max": 300, "required": True},
    "MAX_RETRIES": {"type": "int", "min": 1, "max": 10, "required": True},
    "MAX_SEARCH_RESULTS": {"type": "int", "min": 5, "max": 20, "required": True},
    "TOP_PRODUCTS_COUNT": {"type": "int", "min": 3, "max": 10, "required": True},
    "RATE_LIMIT_PER_MINUTE": {"type": "int", "min": 1, "max": 100, "required": True},
}