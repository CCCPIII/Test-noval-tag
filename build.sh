#!/usr/bin/env bash
# Render 构建脚本：安装后端依赖 + 构建前端
set -e

echo "=== 安装后端依赖 ==="
pip install -r backend/requirements.txt

echo "=== 安装前端依赖 ==="
cd frontend
npm install

echo "=== 构建前端 ==="
npm run build
cd ..

echo "=== 初始化标签库 ==="
python -m scripts.seed_tag_library || true

echo "=== 构建完成 ==="
