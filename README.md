# AI 小说总结与标签生成系统

> 基于大语言模型的小说内容智能分析平台，支持自动生成摘要、多维度标签提取、标签库管理，适配 DeepSeek / Claude / Gemini / 通义千问等 9 种主流 AI 模型。

---

## 项目背景与价值

网络文学行业每年产出海量作品，编辑和运营人员需要快速了解一部小说的核心剧情、风格定位和受众画像。传统人工阅读效率低、标准不统一、成本高。

本系统通过接入大语言模型，实现 **一键生成结构化摘要和多维度标签**，将一部数十万字小说的内容分析时间从数小时缩短至数秒，同时保证输出标签与运营标签体系一致。

**核心指标：**
- 摘要生成：~3 秒 / 篇（短文本单次生成）
- 标签提取：~3 秒 / 篇（5 维度单次 AI 调用）
- 支持百万字级长篇小说分块处理

---

## 核心功能

### 1. 智能摘要生成

- 支持 **50-300 字**自定义目标长度
- 短文本（<8000字）直接生成；长文本自动 **分块 → 逐块摘要 → 合并精炼**
- 摘要支持人工编辑修正，保留完整历史版本
- 生成过程显示 **动态进度条** 和预估剩余时间

### 2. 多维度标签提取

| 维度 | 说明 | 示例 |
|------|------|------|
| 题材 (genre) | 小说类型分类 | 玄幻、都市、悬疑、末世 |
| 风格 (style) | 写作风格特征 | 爽文、慢热、硬核、扮猪吃虎 |
| 元素 (element) | 核心情节元素 | 系统、重生、升级、金手指 |
| 人物 (character) | 角色类型标签 | 废柴逆袭、兵王、腹黑、女强 |
| 专属 (exclusive) | 本作独特标签 | 龙血觉醒、逆天武道 |

- 单次 AI 调用生成全部 5 个维度标签（JSON 格式解析）
- 标签带 **置信度评分**，低置信度自动标记为「争议标签」供人工复核
- 支持手动分配、批量分配、一键移除

### 3. 预置标签库（141 条）

- 内置覆盖 **男频 + 女频** 主流分类的预置标签
- 按维度分组管理，支持增删改查和批量导入
- AI 生成标签时自动参考标签库，确保与运营体系一致
- 应用启动时自动填充，无需手动初始化

### 4. 多模型适配（9 种 AI 服务）

通过统一的 **Client Factory 模式**，一个接口适配所有主流 AI 模型：

| 提供商 | 模型示例 | 协议 |
|--------|---------|------|
| DeepSeek | deepseek-chat / deepseek-reasoner | OpenAI 兼容 |
| OpenAI | gpt-4o / gpt-4o-mini | OpenAI 原生 |
| Anthropic | claude-sonnet-4-20250514 | Claude Messages API |
| Google | gemini-2.0-flash | Gemini REST API |
| 通义千问 | qwen-turbo / qwen-plus | OpenAI 兼容 |
| 豆包 (字节) | doubao-pro-32k | OpenAI 兼容 |
| 月之暗面 | moonshot-v1-8k | OpenAI 兼容 |
| 智谱 AI | glm-4 | ChatGLM API |
| 本地模型 | Ollama / vLLM | OpenAI 兼容 |

- 内置配置指南页面，指导用户填写各模型参数
- 支持 **连接测试**，一键验证 API 是否可用
- API Key **Fernet 加密存储**，运行时解密调用

### 5. 文件处理与导出

- 支持 **TXT / PDF** 格式上传，自动编码检测（UTF-8、GBK 等）
- SHA-256 文件哈希去重，防止重复导入
- 导出支持 **JSON / TXT / DOCX** 格式，支持批量导出

### 6. 搜索与检索

- 按书名模糊搜索
- 按标签组合检索（**AND / OR** 逻辑），快速定位同类作品

---

## 技术架构

```
┌──────────────────────────────────────────────────────┐
│                    Frontend                           │
│          Vue 3 + Element Plus + Pinia + Vite          │
├──────────────────────────────────────────────────────┤
│                    Backend                            │
│      FastAPI + SQLAlchemy (Async) + Pydantic v2       │
│              AI Client Factory 多模型适配层            │
├──────────────────────────────────────────────────────┤
│                    Storage                            │
│     SQLite / MySQL (可切换)  ·  Redis (可选缓存)       │
└──────────────────────────────────────────────────────┘
```

### 后端关键设计

- **全异步架构**：FastAPI + async SQLAlchemy + httpx，高并发无阻塞
- **AI Client Factory 模式**：统一 `create_ai_client()` 接口，通过 `provider` 参数分发到 5 种客户端实现，新增模型仅需添加一个客户端文件
- **API Key 加密存储**：Fernet 对称加密，密钥通过环境变量注入
- **Redis 优雅降级**：未配置 Redis 时自动跳过缓存和进度追踪，不影响核心功能
- **长文本分块策略**：超过 8000 字自动分块 → 逐块摘要 → 合并精炼，支持百万字级小说

### 前端关键设计

- **Vue 3 Composition API** + Pinia 集中式状态管理
- **Element Plus** 组件库，完整中文本地化
- **动态进度反馈**：总结 / 标签生成时显示条纹动画进度条和预估剩余时间
- **Vue Router History 模式**：后端 fallback 到 `index.html` 支持 SPA 路由

---

## API 概览

系统共提供 **36 个 RESTful API 端点**，按业务模块组织：

| 模块 | 端点数 | 说明 |
|------|--------|------|
| 小说管理 | 5 | 文件上传、文本提交、列表、详情、删除 |
| 摘要生成 | 4 | AI 生成、历史查询、人工编辑、进度查询 |
| 标签管理 | 6 | AI 生成、手动分配、批量分配、移除、争议标记 |
| 标签库 | 6 | 列表、分组、添加、批量添加、更新、删除 |
| AI 模型 | 6 | 增删改查、连接测试 |
| 搜索 | 2 | 按名称搜索、按标签检索 |
| 导出 | 2 | 单本导出、批量导出 |
| 用户 | 5 | 注册、登录、个人信息（预留扩展） |

启动后访问 `/docs`（Swagger UI）或 `/redoc` 查看完整交互式 API 文档。

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+

### 本地开发

```bash
# 克隆项目
git clone https://github.com/cccpiii/test-noval-tag.git
cd test-noval-tag

# 后端启动
pip install -r backend/requirements.txt
uvicorn app:app --reload --port 8000

# 前端启动（新终端）
cd frontend
npm install
npm run dev
```

访问 `http://localhost:3000`，前端自动代理 API 请求到后端 8000 端口。

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接串 | `sqlite+aiosqlite:///./novel_tag.db` |
| `REDIS_URL` | Redis 地址（留空则禁用） | `""` |
| `SECRET_KEY` | Fernet 加密密钥 | 自动生成 |
| `UPLOAD_DIR` | 文件上传目录 | `./uploads` |
| `MAX_UPLOAD_SIZE_MB` | 单文件大小限制 | `200` |

### 部署到 Render（免费）

项目已配置 `render.yaml`，支持一键部署：

1. Fork 本仓库到你的 GitHub
2. Render Dashboard → **New → Blueprint** → 选择仓库
3. 自动执行 `build.sh`（安装依赖 + 构建前端 + 初始化标签库）
4. 部署完成后在页面上配置 AI 模型即可使用

---

## 项目结构

```
├── app.py                        # 应用入口
├── build.sh                      # 构建脚本
├── render.yaml                   # Render 部署配置
│
├── backend/
│   ├── main.py                   # FastAPI 初始化、生命周期、路由挂载
│   ├── requirements.txt
│   ├── ai/                       # AI 客户端层
│   │   ├── client_factory.py     #   工厂模式统一创建客户端
│   │   ├── openai_client.py      #   OpenAI / 兼容协议客户端
│   │   ├── claude_client.py      #   Anthropic Claude 客户端
│   │   ├── gemini_client.py      #   Google Gemini 客户端
│   │   ├── zhipu_client.py       #   智谱 ChatGLM 客户端
│   │   └── prompts.py            #   所有 AI 提示词模板
│   ├── core/                     # 核心配置
│   │   ├── config.py             #   环境变量与应用配置
│   │   ├── database.py           #   异步数据库引擎与会话
│   │   ├── redis.py              #   Redis 连接（优雅降级）
│   │   └── dependencies.py       #   FastAPI 依赖注入
│   ├── models/                   # ORM 模型（7 张表）
│   │   ├── novel.py              #   小说
│   │   ├── summary.py            #   摘要
│   │   ├── tag.py                #   标签
│   │   ├── novel_tag.py          #   小说-标签关联（含置信度）
│   │   ├── tag_library.py        #   标签库
│   │   ├── ai_model.py           #   AI 模型配置
│   │   └── user.py               #   用户
│   ├── routers/                  # API 路由（8 个模块）
│   ├── schemas/                  # Pydantic 请求/响应模型
│   └── services/                 # 业务逻辑层
│       ├── summary_service.py    #   摘要生成（短文本 / 分块合并）
│       ├── tag_service.py        #   标签生成与管理
│       ├── tag_library_seed.py   #   141 条预置标签种子数据
│       ├── chunking_service.py   #   文本分块策略
│       ├── file_parser.py        #   TXT / PDF 文件解析
│       ├── dedup_service.py      #   文件去重
│       └── ai_model_service.py   #   AI 模型配置管理
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── views/                # 7 个页面
        │   ├── NovelList.vue     #   小说列表
        │   ├── NovelUpload.vue   #   上传页面
        │   ├── NovelDetail.vue   #   详情（摘要 + 标签）
        │   ├── SearchPage.vue    #   搜索
        │   ├── TagLibrary.vue    #   标签库管理
        │   └── AIModelManage.vue #   AI 模型配置
        ├── components/           # 6 个复用组件
        ├── api/                  # API 调用封装
        ├── stores/               # Pinia 状态管理
        └── router/               # 路由配置
```

---

## 技术栈

| 层级 | 技术选型 |
|------|---------|
| **前端** | Vue 3 · Element Plus · Pinia · Axios · Vite |
| **后端** | Python 3.11 · FastAPI · SQLAlchemy (Async) · Pydantic v2 · httpx |
| **数据库** | SQLite（开发）/ MySQL（生产）· Redis（可选） |
| **AI 接入** | OpenAI API · Anthropic API · Gemini API · 智谱 API · Ollama |
| **安全** | Fernet 加密 · CORS · 文件类型校验 · 哈希去重 |
| **部署** | Render · Uvicorn · 支持任意 Linux / Docker 环境 |

---

## License

MIT
