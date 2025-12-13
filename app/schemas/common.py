"""
通用 Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    errors: Optional[dict] = None


class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list

