"""
FastAPI 应用主文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api, todo

# 创建 FastAPI 应用实例
app = FastAPI(
    title="MyCal API",
    version="1.0.0",
    description="待办事项和日程安排 API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api.router)
app.include_router(todo.router)


@app.get("/", tags=["Root"])
async def root():
    """
    根端点
    """
    return {
        "message": "Welcome to MyCal API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    """
    print("🚀 MyCal API v1.0.0 启动成功")
    print("📚 API 文档: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件
    """
    print("👋 MyCal API 正在关闭...")

