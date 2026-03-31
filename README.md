# AI小说总结与标签生成系统

基于 **FastAPI + Vue 3 + Element Plus** 的AI小说内容分析平台，自动生成小说总结和多维度标签，支持百万字级超长篇小说处理。

---

## 功能特性

### 核心功能
- **文件上传与解析** — 支持 TXT、PDF 格式，单文件最大 200MB，批量上传最多 10 个
- **AI总结生成** — 可配置长度（50-300字），超长篇自动分段处理后合并
- **多维度标签生成** — 题材、风格、核心元素、人物类型 4 大维度 + 1-2 个专属标签
- **传统标签库** — 预置 70+ 标签，支持人工补充，AI 生成时自动参考
- **争议标签** — 可标记争议标签并添加悬浮解释说明
- **智能去重** — SHA-256 文件哈希比对，避免重复上传和处理
- **双模式搜索** — 名称搜索（精准/模糊）+ 标签搜索（单个/多标签组合）
- **结果导出** — 支持 TXT、Word 格式导出，支持批量导出

### 扩展功能
- **AI模型管理** — 支持配置多个AI模型（OpenAI、智谱AI、本地模型等），自由切换
- **用户模块（预留）** — 登录、收藏、个人中心接口已预留，待后续开发
- **超长篇优化** — 分段解析、分段总结、进度实时展示，适配百万字级小说

---

## 技术架构

```
┌─────────────────────────────────────────────┐
│                前端展示层                      │
│         Vue 3 + Element Plus + Vite          │
├─────────────────────────────────────────────┤
│                后端服务层                      │
│           Python + FastAPI (RESTful)          │
├──────────────────┬──────────────────────────┤
│    AI核心层       │      数据存储层            │
│  多模型客户端     │   MySQL + Redis           │
│  提示词模板       │   SQLAlchemy ORM          │
└──────────────────┴──────────────────────────┘
```

### 后端模块

| 目录 | 说明 |
|------|------|
| `backend/core/` | 配置管理、数据库连接、Redis连接、依赖注入 |
| `backend/models/` | 7 个 ORM 模型（小说、总结、标签、标签库、AI模型、用户等） |
| `backend/schemas/` | Pydantic 请求/响应模型 |
| `backend/routers/` | 8 个 API 路由（小说、总结、标签、搜索、导出、AI模型等） |
| `backend/services/` | 11 个业务服务（文件解析、分段处理、去重、搜索、导出等） |
| `backend/ai/` | AI 客户端（OpenAI/智谱/本地）、提示词模板、工厂模式 |
| `backend/utils/` | 加密工具、文件工具、分页工具 |

### 前端模块

| 目录 | 说明 |
|------|------|
| `frontend/src/views/` | 7 个页面（列表、上传、详情、搜索、标签库、AI模型、用户） |
| `frontend/src/components/` | 6 个复用组件（总结面板、标签展示/编辑、导出、进度条等） |
| `frontend/src/api/` | 7 个 API 接口模块 |
| `frontend/src/stores/` | Pinia 状态管理 |

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+（或 SQLite 用于本地测试）
- Redis 7.0+

### 1. 后端启动

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库地址、Redis地址等

# 启动服务
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

### 3. Docker 一键启动

```bash
docker-compose up -d
```

自动启动 MySQL + Redis + 后端服务。

### 4. 初始化标签库

```bash
python -m scripts.seed_tag_library
```

预置 70+ 常用小说标签（题材、风格、核心元素、人物类型）。

---

## API 文档

启动后端后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/novels/upload` | 上传小说文件 |
| POST | `/api/v1/novels/text` | 提交小说文本 |
| GET | `/api/v1/novels/` | 小说列表 |
| GET | `/api/v1/novels/{id}` | 小说详情 |
| POST | `/api/v1/novels/{id}/summary/generate` | 生成总结 |
| POST | `/api/v1/novels/{id}/tags/generate` | 生成标签 |
| GET | `/api/v1/search/by-name` | 名称搜索 |
| GET | `/api/v1/search/by-tags` | 标签搜索 |
| POST | `/api/v1/export/{id}` | 导出结果 |
| GET | `/api/v1/tag-library/` | 标签库管理 |
| GET | `/api/v1/ai-models/` | AI模型管理 |

---

## 项目结构

```
Test-noval-tag/
├── backend/
│   ├── main.py                 # FastAPI 应用入口
│   ├── requirements.txt
│   ├── core/                   # 核心配置
│   ├── models/                 # 数据模型
│   ├── schemas/                # 请求/响应模型
│   ├── routers/                # API 路由
│   ├── services/               # 业务逻辑
│   ├── ai/                     # AI 模型集成
│   └── utils/                  # 工具函数
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── router/             # 路由配置
│       ├── api/                # API 接口
│       ├── views/              # 页面组件
│       ├── components/         # 复用组件
│       ├── stores/             # 状态管理
│       └── styles/             # 全局样式
├── scripts/
│   ├── init_db.sql             # 数据库初始化
│   └── seed_tag_library.py     # 标签库种子数据
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## 配置说明

编辑 `.env` 文件：

```env
# 数据库（MySQL 或 SQLite）
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/novel_tag_db
# DATABASE_URL=sqlite+aiosqlite:///./novel_tag.db  # 本地测试用

# Redis
REDIS_URL=redis://localhost:6379/0

# 文件上传
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=200

# AI 总结默认长度
DEFAULT_SUMMARY_LENGTH=100

# API Key 加密密钥
ENCRYPTION_KEY=你的32位十六进制密钥

# 分段处理配置（适配超长篇小说）
CHUNK_SIZE=8000
CHUNK_OVERLAP=500
```

---

## 开发说明

- 后端遵循 **分层架构**：Router -> Service -> Model，模块间通过接口解耦
- 前端使用 **Vue 3 Composition API** + **Element Plus** 组件库
- 所有接口遵循 **RESTful** 规范，完整保留，便于后续移植到移动端/桌面端
- AI 模型通过 **工厂模式** 封装，新增模型只需添加一个客户端文件
- 超长篇处理采用 **分段解析 + 分段总结 + 合并** 策略
