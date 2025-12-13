"""
API 路由示例
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.schemas.common import (
    HealthCheckResponse,
    MessageResponse,
    PaginationParams
)
from app.utils.response import ResponseModel
from app.dependencies import get_current_user, get_optional_user

router = APIRouter(prefix="/api/v1", tags=["API"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    健康检查端点
    """
    return HealthCheckResponse()


@router.get("/hello", response_model=dict)
async def hello(
    name: Optional[str] = Query(default="World", description="名称")
):
    """
    示例问候端点
    """
    return ResponseModel.success(
        data={"message": f"Hello, {name}!"},
        message="问候成功"
    )


@router.get("/protected", response_model=dict)
async def protected_route(
    current_user: dict = Depends(get_current_user)
):
    """
    需要认证的受保护端点示例
    """
    return ResponseModel.success(
        data={
            "user": current_user,
            "message": "这是一个受保护的端点"
        },
        message="访问成功"
    )


@router.get("/optional-auth", response_model=dict)
async def optional_auth_route(
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    可选认证的端点示例
    """
    if current_user:
        message = f"欢迎回来, {current_user.get('username')}!"
    else:
        message = "欢迎，访客！"
    
    return ResponseModel.success(
        data={"message": message},
        message="访问成功"
    )


@router.get("/items", response_model=dict)
async def get_items(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="搜索关键词")
):
    """
    获取项目列表（带分页）
    """
    # 示例数据
    all_items = [
        {"id": i, "name": f"Item {i}", "description": f"Description for item {i}"}
        for i in range(1, 101)
    ]
    
    # 搜索过滤
    if search:
        all_items = [item for item in all_items if search.lower() in item["name"].lower()]
    
    # 分页计算
    total = len(all_items)
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    start = (pagination.page - 1) * pagination.page_size
    end = start + pagination.page_size
    
    items = all_items[start:end]
    
    return ResponseModel.success(
        data={
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": total_pages,
            "items": items
        },
        message="获取成功"
    )

