# Novel Copilot - AI 小说写作辅助工具

基于 RAG (检索增强生成) 技术的 AI 小说写作辅助工具，支持智能大纲生成和章节创作。

## 功能特点

- **智能写作生成**: 基于大纲和设定自动生成小说章节
- **知识库管理**: 支持项目设定、上下文、背景知识的分类管理
- **多模型支持**: 支持多种 LLM 提供商（OpenAI、DeepSeek、SiliconFlow、DashScope、Ollama）
- **灵活配置**: 可自定义生成参数和模型选择
- **RAG 检索**: 智能检索相关知识，提升生成质量

## 项目架构

```
novel/
├── main.py                    # Streamlit 主入口
│
├── app/                       # 应用层（UI）
│   ├── pages/                 # Streamlit 页面
│   │   ├── 1_写作生成.py
│   │   ├── 2_项目管理.py
│   │   └── 3_系统设置.py
│   └── components/            # UI 组件
│       ├── input_card.py      # 输入卡片组件
│       ├── file_manager.py    # 文件管理组件
│       └── model_selector.py  # 模型选择组件
│
├── core/                      # 核心业务层
│   ├── workflows/             # 业务工作流
│   │   └── novel_workflow.py  # 小说生成工作流
│   └── services/              # 业务服务（待扩展）
│
├── llm/                       # LLM 层
│   ├── providers/             # LLM 提供商
│   │   └── base.py            # LLM 基类
│   └── generators/            # 生成器（含提示词）
│       ├── novel_generator.py      # 小说生成器
│       ├── outline_generator.py    # 大纲生成器
│       ├── queries_extractor.py    # 查询提取器
│       └── content_shorter.py      # 内容缩写器
│
├── rag/                       # RAG 层
│   ├── processors.py          # 文档处理器
│   └── retrievers.py          # 检索器
│
├── config/                    # 配置层
│   ├── settings.py            # 应用配置
│   └── project_config.py      # 项目配置管理
│
├── utils/                     # 工具层
│   ├── file_utils.py          # 文件操作工具
│   └── export_utils.py        # 导出工具
│
└── data/                      # 数据目录
    ├── knowledgebase/         # 知识库
    └── projects/              # 项目配置文件
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd novel

# 安装依赖（使用 uv 或 pip）
uv sync
# 或
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 2. 配置 API 密钥

在 `.env` 文件中配置你使用的 LLM 提供商的 API 密钥：

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# SiliconFlow
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# DashScope (阿里云)
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# Ollama (本地部署)
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. 运行应用

```bash
streamlit run main.py
```

应用将在浏览器中打开（默认地址：http://localhost:8501）

## 使用指南

### 创建项目

1. 进入 **项目管理** 页面
2. 在项目选择框中输入新项目名称
3. 点击 **新建项目** 按钮
4. 上传相关知识库文件（小说大纲、角色设定、背景资料等）

### 生成小说

1. 进入 **写作生成** 页面
2. 选择已创建的项目
3. 填写生成要求和大纲描述
4. 选择模型和配置参数
5. 点击 **自动生成大纲** 或 **自动生成章节**

### 知识库管理

项目支持三类知识库：

- **项目知识库**: 存放小说大纲、角色设定、装备设定等
- **上下文知识库**: 存放已生成的章节内容，用于保持上下文一致性
- **背景知识库**: 存放世界观、历史背景等通用知识

## Docker 部署

### Windows 一键部署（推荐）

双击运行 `deploy.bat` 即可完成部署。

详细说明请参考：[Docker 部署指南](DOCKER_DEPLOYMENT.md)

### 手动部署

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 2. 创建数据目录
mkdir -p data/db data/vectordb data/files

# 3. 启动服务
docker compose up -d

# 4. 访问应用
# http://localhost:8501
```

### 数据持久化

所有数据都会保存在 `data/` 目录：
- `data/db/` - SQLite 数据库
- `data/vectordb/` - 向量数据库
- `data/files/` - 用户上传的文件

## 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│         应用层 (app/)               │
│  - Streamlit 页面                   │
│  - UI 组件                          │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│       核心业务层 (core/)            │
│  - 工作流编排 (workflows/)          │
│  - 业务服务 (services/)             │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         LLM 层 (llm/)               │
│  - LLM 提供商 (providers/)          │
│  - 生成器 (generators/)             │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         RAG 层 (rag/)               │
│  - 文档处理器                       │
│  - 检索器                           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       基础设施层                    │
│  - 配置层 (config/)                 │
│  - 工具层 (utils/)                  │
│  - 数据层 (data/)                   │
└─────────────────────────────────────┘
```

### 依赖规则

- 上层可以依赖下层，下层不能依赖上层
- 同层之间尽量减少依赖
- 核心业务层不依赖应用层（便于测试和复用）

## 技术栈

- **Web 框架**: Streamlit
- **LLM 框架**: LangChain
- **向量数据库**: Chroma
- **文档处理**: LangChain Document Loaders
- **Python 版本**: 3.12+

## 开发指南

### 添加新的生成器

1. 在 `llm/generators/` 下创建新的生成器文件
2. 继承 `LLM` 基类
3. 定义提示词模板和响应 schema
4. 实现 `__init__` 方法

### 添加新的工作流

1. 在 `core/workflows/` 下创建新的工作流文件
2. 使用生成器和检索器组合业务逻辑
3. 提供 `progress_callback` 参数以支持进度反馈

### 添加新的 UI 组件

1. 在 `app/components/` 下创建新的组件文件
2. 使用 Streamlit 组件 API
3. 保持组件的可复用性

## 许可证

MIT License

## 维护者

ersonlzy@qq.com

## 贡献

欢迎提交 Issue 和 Pull Request！
