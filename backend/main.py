"""
应用入口
FastAPI 应用初始化、生命周期管理、路由挂载
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.database import init_db
from backend.core.redis import init_redis, close_redis

# 确保所有模型在 metadata 中注册
import backend.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化资源，关闭时释放资源"""
    # ---- 启动阶段 ----
    # 初始化数据库（建表）
    await init_db()
    # 初始化 Redis 连接
    await init_redis()
    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    yield

    # ---- 关闭阶段 ----
    await close_redis()


app = FastAPI(
    title="AI 小说摘要与标签生成系统",
    description="上传小说文件，自动生成摘要和标签",
    version="1.0.0",
    lifespan=lifespan,
)

# 跨域中间件配置（开发阶段允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载上传文件的静态资源目录
if os.path.isdir(settings.UPLOAD_DIR):
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="uploads",
    )

# ---- 挂载路由 ----
from backend.routers import novel as novel_router
from backend.routers import summary as summary_router
from backend.routers import tag as tag_router
from backend.routers import tag_library as tag_library_router
from backend.routers import search as search_router
from backend.routers import export as export_router
from backend.routers import ai_model as ai_model_router
from backend.routers import user as user_router

app.include_router(novel_router.router, prefix="/api/v1")
app.include_router(summary_router.router, prefix="/api/v1")
app.include_router(tag_router.router, prefix="/api/v1")
app.include_router(tag_library_router.router, prefix="/api/v1")
app.include_router(search_router.router, prefix="/api/v1")
app.include_router(export_router.router, prefix="/api/v1")
app.include_router(ai_model_router.router, prefix="/api/v1")
app.include_router(user_router.router, prefix="/api/v1")


@app.get("/", tags=["健康检查"])
async def root():
    """根路径健康检查"""
    return {"message": "AI 小说摘要与标签生成系统运行中", "status": "ok"}


@app.get("/api/v1/health", tags=["健康检查"])
async def health_check():
    """API 健康检查端点"""
    return {"status": "healthy"}
