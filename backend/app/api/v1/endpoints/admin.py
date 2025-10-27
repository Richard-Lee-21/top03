"""
管理员API端点
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError, ValidationError
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse
from app.schemas.configuration import Configuration, ConfigurationBatchUpdate
from app.services.configuration import ConfigurationService

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """验证JWT令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        if username != settings.ADMIN_USERNAME:
            raise AuthorizationError("Invalid user")

        return username

    except JWTError:
        raise credentials_exception


def get_current_admin(username: str = Depends(verify_token)):
    """获取当前管理员"""
    return username


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """管理员登录"""
    try:
        # 验证用户名和密码
        if request.username != settings.ADMIN_USERNAME:
            raise AuthenticationError("用户名或密码错误")

        # 在实际应用中，这里应该验证哈希密码
        # 为了简化，我们直接比较明文密码
        if request.password != settings.ADMIN_PASSWORD:
            raise AuthenticationError("用户名或密码错误")

        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": request.username},
            expires_delta=access_token_expires
        )

        logger.info(f"Admin '{request.username}' logged in successfully")

        return AdminLoginResponse(
            status="success",
            token=access_token,
            expires_in=settings.JWT_EXPIRE_MINUTES * 60  # 转换为秒
        )

    except AuthenticationError as e:
        logger.warning(f"Failed login attempt for user '{request.username}': {e.message}")
        raise HTTPException(status_code=401, detail={
            "status": "error",
            "message": e.message,
            "code": e.code
        })
    except Exception as e:
        logger.error(f"Unexpected error in admin login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "登录失败，请稍后重试",
            "code": "INTERNAL_SERVER_ERROR"
        })


@router.get("/settings", response_model=List[Configuration])
async def get_settings(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有配置项"""
    try:
        config_service = ConfigurationService(db)
        configurations = await config_service.get_all_configurations()
        return configurations

    except Exception as e:
        logger.error(f"Failed to get settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "获取配置失败",
            "code": "INTERNAL_SERVER_ERROR"
        })


@router.post("/settings")
async def update_settings(
    request: ConfigurationBatchUpdate,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """批量更新配置项"""
    try:
        if not request.settings or len(request.settings) == 0:
            raise ValidationError("配置项列表不能为空")

        config_service = ConfigurationService(db)

        # 验证每个配置项
        for setting in request.settings:
            if not setting.get("key") or not setting.get("value"):
                raise ValidationError("配置项必须包含key和value")

            # 验证配置值
            is_valid = await config_service.validate_configuration_value(
                setting["key"],
                setting["value"]
            )
            if not is_valid:
                raise ValidationError(f"配置项 '{setting['key']}' 的值 '{setting['value']}' 无效")

        # 更新配置
        updated_configurations = await config_service.batch_update_configurations(request.settings)

        logger.info(f"Admin '{current_admin}' updated {len(updated_configurations)} configurations")

        return {
            "status": "success",
            "message": f"成功更新 {len(updated_configurations)} 个配置项"
        }

    except ValidationError as e:
        logger.warning(f"Validation error in update settings: {e.message}")
        raise HTTPException(status_code=400, detail={
            "status": "error",
            "message": e.message,
            "code": e.code
        })
    except Exception as e:
        logger.error(f"Failed to update settings: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "更新配置失败",
            "code": "INTERNAL_SERVER_ERROR"
        })


@router.post("/initialize-seed")
async def initialize_seed_data(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """初始化种子数据"""
    try:
        config_service = ConfigurationService(db)
        configurations = await config_service.initialize_seed_data()

        logger.info(f"Admin '{current_admin}' initialized seed data")

        return {
            "status": "success",
            "message": f"成功初始化 {len(configurations)} 个配置项",
            "data": {
                "count": len(configurations),
                "configurations": [config.to_dict() for config in configurations]
            }
        }

    except Exception as e:
        logger.error(f"Failed to initialize seed data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": "初始化种子数据失败",
            "code": "INTERNAL_SERVER_ERROR"
        })


@router.get("/health")
async def admin_health_check(current_admin: str = Depends(get_current_admin)):
    """管理员健康检查"""
    return {
        "status": "success",
        "message": "Admin endpoint is working",
        "user": current_admin,
        "timestamp": datetime.utcnow().isoformat()
    }