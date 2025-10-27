"""
配置数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Configuration(Base):
    """配置表模型"""
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True, comment="配置项的唯一键")
    value = Column(Text, nullable=False, comment="配置项的值")
    group = Column(String(50), nullable=False, index=True, comment="配置组 (api, prompt, ui, cache)")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

    def __repr__(self):
        return f"<Configuration(key='{self.key}', group='{self.group}')>"

    @classmethod
    def get_groups(cls):
        """获取所有可用的配置组"""
        return ["api", "prompt", "ui", "cache"]

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "group": self.group,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }