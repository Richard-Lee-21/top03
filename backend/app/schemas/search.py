"""
搜索相关的Pydantic模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """搜索请求模型"""
    keyword: str = Field(..., min_length=1, max_length=200, description="商品关键词")

    class Config:
        schema_extra = {
            "example": {
                "keyword": "无线蓝牙耳机"
            }
        }


class ProductRecommendation(BaseModel):
    """商品推荐模型"""
    rank: int = Field(..., ge=1, le=3, description="推荐排名")
    product_name: str = Field(..., description="商品名称")
    description: str = Field(..., description="推荐理由和描述")
    source_link: str = Field(..., description="来源链接")
    price: Optional[str] = Field(None, description="价格信息")
    rating: Optional[float] = Field(None, ge=0, le=5, description="评分 (0-5)")
    image_url: Optional[str] = Field(None, description="商品图片链接")
    pros: Optional[List[str]] = Field(None, description="优点列表")
    cons: Optional[List[str]] = Field(None, description="缺点列表")
    best_for: Optional[str] = Field(None, description="适合人群")

    class Config:
        schema_extra = {
            "example": {
                "rank": 1,
                "product_name": "Sony WH-1000XM5 无线降噪耳机",
                "description": "业界领先的降噪技术，出色的音质表现，舒适佩戴体验",
                "source_link": "https://example.com/review",
                "price": "¥2,499",
                "rating": 4.8,
                "pros": [
                    "顶级的主动降噪效果",
                    "30小时超长续航",
                    "佩戴舒适度高"
                ],
                "cons": [
                    "价格相对较高",
                    "折叠后体积较大"
                ],
                "best_for": "对音质和降噪有高要求的商务人士和音乐爱好者"
            }
        }


class SearchResponse(BaseModel):
    """搜索响应模型"""
    products: List[ProductRecommendation] = Field(..., description="推荐商品列表")
    total_results: int = Field(..., ge=0, description="搜索结果总数")
    search_time: float = Field(..., ge=0, description="搜索耗时(秒)")
    cached: bool = Field(..., description="是否来自缓存")

    class Config:
        schema_extra = {
            "example": {
                "products": [
                    {
                        "rank": 1,
                        "product_name": "Sony WH-1000XM5",
                        "description": "优秀的降噪耳机",
                        "source_link": "https://example.com",
                        "price": "¥2,499",
                        "rating": 4.8
                    }
                ],
                "total_results": 15,
                "search_time": 2.34,
                "cached": False
            }
        }


class SearchResultItem(BaseModel):
    """单个搜索结果项（来自外部API）"""
    title: str = Field(..., description="标题")
    link: str = Field(..., description="链接")
    snippet: str = Field(..., description="摘要")
    position: int = Field(..., ge=1, description="位置")
    favicon: Optional[str] = Field(None, description="网站图标")
    date: Optional[str] = Field(None, description="发布日期")