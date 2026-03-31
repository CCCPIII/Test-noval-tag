"""Render 启动入口 — 确保项目根目录在 sys.path 中"""
import sys
from pathlib import Path

# 把项目根目录加入 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.main import app  # noqa: E402, F401
