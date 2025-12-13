"""
响应工具函数
"""

from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status


class ResponseModel:
    """统一响应模型"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = 200
    ) -> dict:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: 响应代码
            
        Returns:
            统一格式的响应字典
        """
        return {
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 400,
        errors: Optional[dict] = None
    ) -> dict:
        """
        错误响应
        
        Args:
            message: 错误消息
            code: 错误代码
            errors: 详细错误信息
            
        Returns:
            统一格式的错误响应字典
        """
        response = {
            "code": code,
            "message": message
        }
        if errors:
            response["errors"] = errors
        return response


def success_response(
    data: Any = None,
    message: str = "操作成功",
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    返回成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP 状态码
        
    Returns:
        JSONResponse 对象
    """
    return JSONResponse(
        status_code=status_code,
        content=ResponseModel.success(data=data, message=message, code=status_code)
    )


def error_response(
    message: str = "操作失败",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[dict] = None
) -> JSONResponse:
    """
    返回错误响应
    
    Args:
        message: 错误消息
        status_code: HTTP 状态码
        errors: 详细错误信息
        
    Returns:
        JSONResponse 对象
    """
    return JSONResponse(
        status_code=status_code,
        content=ResponseModel.error(message=message, code=status_code, errors=errors)
    )

