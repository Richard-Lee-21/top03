"""
管理员相关的Pydantic模型
"""

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., min_length=1, description="密码")

    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "password": "secure_password"
            }
        }


class AdminLoginResponse(BaseModel):
    """管理员登录响应"""
    status: str = Field("success", description="状态")
    token: str = Field(..., description="JWT令牌")
    expires_in: int = Field(..., description="过期时间(秒)")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_in": 86400
            }
        }