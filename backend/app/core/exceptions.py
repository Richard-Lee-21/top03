"""
自定义异常类
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """应用基础异常类"""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)


class ValidationError(AppException):
    """数据验证错误"""

    def __init__(self, message: str = "数据验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(AppException):
    """认证错误"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            status_code=401,
            code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(AppException):
    """授权错误"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=403,
            code="AUTHORIZATION_ERROR"
        )


class NotFoundError(AppException):
    """资源未找到错误"""

    def __init__(self, message: str = "资源未找到"):
        super().__init__(
            message=message,
            status_code=404,
            code="NOT_FOUND"
        )


class ConflictError(AppException):
    """资源冲突错误"""

    def __init__(self, message: str = "资源冲突"):
        super().__init__(
            message=message,
            status_code=409,
            code="CONFLICT"
        )


class RateLimitError(AppException):
    """频率限制错误"""

    def __init__(self, message: str = "请求过于频繁，请稍后重试"):
        super().__init__(
            message=message,
            status_code=429,
            code="RATE_LIMIT_EXCEEDED"
        )


class ExternalAPIError(AppException):
    """外部API调用错误"""

    def __init__(
        self,
        message: str = "外部服务调用失败",
        service_name: str = "unknown",
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=status_code,
            code="EXTERNAL_API_ERROR",
            details=details
        )
        self.service_name = service_name


class SearchAPIError(ExternalAPIError):
    """搜索API错误"""

    def __init__(self, message: str = "搜索服务调用失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            service_name="Search API",
            status_code=502,
            details=details
        )


class LLMAPIError(ExternalAPIError):
    """LLM API错误"""

    def __init__(self, message: str = "AI分析服务调用失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            service_name="LLM API",
            status_code=502,
            details=details
        )


class CacheError(AppException):
    """缓存操作错误"""

    def __init__(self, message: str = "缓存操作失败"):
        super().__init__(
            message=message,
            status_code=500,
            code="CACHE_ERROR"
        )


class DatabaseError(AppException):
    """数据库操作错误"""

    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(
            message=message,
            status_code=500,
            code="DATABASE_ERROR"
        )


class ConfigurationError(AppException):
    """配置错误"""

    def __init__(self, message: str = "配置错误"):
        super().__init__(
            message=message,
            status_code=500,
            code="CONFIGURATION_ERROR"
        )


class BusinessLogicError(AppException):
    """业务逻辑错误"""

    def __init__(self, message: str = "业务逻辑错误", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            code="BUSINESS_LOGIC_ERROR",
            details=details
        )