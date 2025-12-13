"""
FastAPI 依赖项
"""

from fastapi import Depends, HTTPException, status
from typing import Optional

# 简单的用户认证依赖（示例）
# 在实际项目中，这里应该实现真正的认证逻辑


async def get_current_user() -> dict:
    """
    获取当前用户（示例依赖项）
    在实际项目中，这里应该验证 token 并返回用户信息
    """
    # 示例：返回用户信息
    return {
        "id": 1,
        "username": "example_user",
        "email": "user@example.com"
    }


async def get_optional_user() -> Optional[dict]:
    """
    获取可选用户（用于可选认证的端点）
    """
    # 示例：返回用户信息
    return {
        "id": 1,
        "username": "example_user",
        "email": "user@example.com"
    }

