"""
应用入口
FastAPI 应用初始化、生命周期管理、路由挂载
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.core.config import settings
from backend.core.database import init_db
from backend.core.redis import init_redis, close_redis

# 确保所有模型在 metadata 中注册
import backend.models  # noqa: F401

# 前端构建产物目录
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化资源，关闭时释放资源"""
    await init_db()
    await init_redis()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    yield

    await close_redis()


app = FastAPI(
    title="AI 小说摘要与标签生成系统",
    description="上传小说文件，自动生成摘要和标签",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载上传文件的静态资源目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads",
)

# ---- 挂载 API 路由 ----
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


@app.get("/api/v1/health", tags=["健康检查"])
async def health_check():
    """API 健康检查端点"""
    return {"status": "healthy"}


# ---- 前端静态文件托管 ----
if FRONTEND_DIST.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="frontend-assets",
    )

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """所有非 API 路径返回前端 index.html，支持 Vue Router history 模式"""
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/", tags=["健康检查"])
    async def root():
        return {"message": "AI 小说摘要与标签生成系统运行中（前端未构建）", "status": "ok"}
