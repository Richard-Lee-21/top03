"""
配置服务
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.configuration import Configuration
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.core.seed_data import (
    get_seed_configurations,
    validate_required_configurations,
    CONFIG_GROUP_DESCRIPTIONS
)

logger = logging.getLogger(__name__)


class ConfigurationService:
    """配置服务类"""

    def __init__(self, db: Session):
        self.db = db

    async def get_all_configurations(self) -> List[Configuration]:
        """获取所有配置项"""
        try:
            configurations = self.db.query(Configuration).all()
            logger.info(f"Retrieved {len(configurations)} configurations")
            return configurations
        except Exception as e:
            logger.error(f"Failed to retrieve configurations: {e}")
            raise

    async def get_configuration_by_key(self, key: str) -> Optional[Configuration]:
        """根据键获取配置项"""
        try:
            configuration = self.db.query(Configuration).filter(
                Configuration.key == key
            ).first()

            if not configuration:
                raise NotFoundError(f"配置项 '{key}' 不存在")

            return configuration
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get configuration by key '{key}': {e}")
            raise

    async def get_configurations_by_group(self, group: str) -> List[Configuration]:
        """根据组获取配置项列表"""
        try:
            configurations = self.db.query(Configuration).filter(
                Configuration.group == group
            ).all()

            logger.info(f"Retrieved {len(configurations)} configurations for group '{group}'")
            return configurations
        except Exception as e:
            logger.error(f"Failed to retrieve configurations for group '{group}': {e}")
            raise

    async def create_configuration(self, config_data: Dict[str, Any]) -> Configuration:
        """创建配置项"""
        try:
            configuration = Configuration(
                key=config_data["key"],
                value=config_data["value"],
                group=config_data["group"]
            )

            self.db.add(configuration)
            self.db.commit()
            self.db.refresh(configuration)

            logger.info(f"Created configuration: {configuration.key}")
            return configuration

        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e).lower():
                raise ConflictError(f"配置项 '{config_data['key']}' 已存在")
            logger.error(f"Integrity error creating configuration: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create configuration: {e}")
            raise

    async def update_configuration(self, key: str, value: str) -> Configuration:
        """更新配置项"""
        try:
            configuration = await self.get_configuration_by_key(key)
            configuration.value = value

            self.db.commit()
            self.db.refresh(configuration)

            logger.info(f"Updated configuration: {configuration.key}")
            return configuration

        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update configuration '{key}': {e}")
            raise

    async def batch_update_configurations(self, settings: List[Dict[str, str]]) -> List[Configuration]:
        """批量更新配置项"""
        updated_configurations = []
        errors = []

        try:
            for setting in settings:
                try:
                    configuration = await self.update_configuration(
                        key=setting["key"],
                        value=setting["value"]
                    )
                    updated_configurations.append(configuration)
                except NotFoundError:
                    # 如果配置项不存在，创建新的
                    try:
                        configuration = await self.create_configuration({
                            "key": setting["key"],
                            "value": setting["value"],
                            "group": "api"  # 默认组
                        })
                        updated_configurations.append(configuration)
                    except Exception as e:
                        errors.append(f"Failed to create configuration '{setting['key']}': {e}")
                        continue
                except Exception as e:
                    errors.append(f"Failed to update configuration '{setting['key']}': {e}")
                    continue

            if errors:
                logger.warning(f"Some configurations failed to update: {errors}")

            logger.info(f"Batch updated {len(updated_configurations)} configurations")
            return updated_configurations

        except Exception as e:
            logger.error(f"Failed to batch update configurations: {e}")
            raise

    async def delete_configuration(self, key: str) -> bool:
        """删除配置项"""
        try:
            configuration = await self.get_configuration_by_key(key)

            self.db.delete(configuration)
            self.db.commit()

            logger.info(f"Deleted configuration: {configuration.key}")
            return True

        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete configuration '{key}': {e}")
            raise

    async def initialize_seed_data(self) -> List[Configuration]:
        """初始化种子数据"""
        try:
            # 检查是否已有配置数据
            existing_count = self.db.query(Configuration).count()
            if existing_count > 0:
                logger.info(f"Database already has {existing_count} configurations, skipping seed initialization")
                return await self.get_all_configurations()

            # 获取种子数据
            seed_configurations = get_seed_configurations()
            created_configurations = []

            for config in seed_configurations:
                try:
                    created_config = await self.create_configuration({
                        "key": config.key,
                        "value": config.value,
                        "group": config.group
                    })
                    created_configurations.append(created_config)
                except Exception as e:
                    logger.error(f"Failed to create seed configuration '{config.key}': {e}")
                    continue

            logger.info(f"Initialized {len(created_configurations)} seed configurations")

            # 验证必需配置
            missing_configs = validate_required_configurations(created_configurations)
            if missing_configs:
                logger.warning(f"Missing required configurations: {missing_configs}")

            return created_configurations

        except Exception as e:
            logger.error(f"Failed to initialize seed data: {e}")
            raise

    async def get_configuration_dict(self) -> Dict[str, str]:
        """获取配置字典（键值对）"""
        try:
            configurations = await self.get_all_configurations()
            config_dict = {config.key: config.value for config in configurations}
            return config_dict
        except Exception as e:
            logger.error(f"Failed to get configuration dict: {e}")
            raise

    async def get_groups(self) -> Dict[str, str]:
        """获取所有配置组及描述"""
        return CONFIG_GROUP_DESCRIPTIONS.copy()

    async def validate_configuration_value(self, key: str, value: str) -> bool:
        """验证配置值是否有效"""
        from app.core.seed_data import CONFIG_VALIDATION_RULES

        if key not in CONFIG_VALIDATION_RULES:
            return True

        rule = CONFIG_VALIDATION_RULES[key]

        try:
            if rule.get("type") == "int":
                int_value = int(value)
                if "min" in rule and int_value < rule["min"]:
                    return False
                if "max" in rule and int_value > rule["max"]:
                    return False
            elif "values" in rule:
                if value not in rule["values"]:
                    return False

            return True
        except (ValueError, TypeError):
            return False