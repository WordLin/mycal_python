"""
应用入口文件
使用 uvicorn 运行: uvicorn main:app --reload
"""

from app.main import app

__all__ = ["app"]
