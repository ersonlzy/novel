# Novel Copilot - 客户部署指南

欢迎使用 Novel Copilot AI 小说写作辅助工具！本指南将帮助您快速完成部署。

---

## 📦 部署包内容

解压后，您将看到以下文件和目录：

```
novel-copilot/
├── app/                     # 应用界面代码
├── core/                    # 核心业务逻辑
├── llm/                     # 大语言模型集成
├── rag/                     # RAG 检索系统
├── config/                  # 系统配置
├── utils/                   # 工具函数
├── pages/                   # 页面文件
├── data/                    # 数据目录（自动创建）
│   ├── db/                  # 数据库存储
│   ├── vectordb/            # 向量数据库
│   └── files/               # 用户文件
├── main.py                  # 主程序入口
├── Dockerfile               # Docker 镜像配置
├── docker-compose.yml       # Docker 编排配置
├── deploy.bat               # ⭐ Windows 一键部署脚本
├── stop.bat                 # 停止服务脚本
├── restart.bat              # 重启服务脚本
├── logs.bat                 # 查看日志脚本
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
├── README.md                # 项目说明
└── DOCKER_DEPLOYMENT.md     # Docker 详细部署文档
```

---

## 🚀 快速部署（3 步完成）

### 前置要求

- **操作系统**: Windows 10/11 64位
- **Docker Desktop**: [点击下载](https://www.docker.com/products/docker-desktop)
- **内存**: 至少 4GB 可用内存
- **磁盘**: 至少 10GB 可用空间

### 第一步：安装 Docker Desktop

1. 从 https://www.docker.com/products/docker-desktop 下载 Docker Desktop
2. 运行安装程序并按提示完成安装
3. **重启电脑**（必须）
4. 启动 Docker Desktop，等待其完全启动（托盘图标变绿）

### 第二步：配置 API 密钥

1. 将 `.env.example` 重命名为 `.env`
2. 使用记事本打开 `.env` 文件
3. 填入您的大语言模型 API 密钥：

```env
# 示例配置 - 请替换为您的真实 API Key

# OpenAI（推荐）
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_API_KEY = "sk-your-actual-api-key-here"

# DeepSeek（国内推荐）
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_API_KEY = "sk-your-actual-api-key-here"

# 其他模型（可选）
SILICONFLOW_API_KEY = "sk-your-actual-api-key-here"
DASHSCOPE_API_KEY = "sk-your-actual-api-key-here"
```

**重要提示**：
- 至少需要配置一个模型的 API Key
- 推荐使用 DeepSeek（性价比高）或 OpenAI（效果好）
- 保存文件后关闭

### 第三步：一键部署

1. **双击运行** `deploy.bat` 文件
2. 脚本会自动完成以下操作：
   - ✅ 检查 Docker 环境
   - ✅ 创建数据目录
   - ✅ 构建 Docker 镜像
   - ✅ 启动服务
   - ✅ 打开浏览器
3. 等待部署完成（首次部署约需 5-10 分钟）
4. 浏览器会自动打开 `http://localhost:8501`

**完成！** 🎉 您现在可以开始使用 Novel Copilot！

---

## 📖 使用说明

### 创建第一个小说项目

1. 点击左侧导航栏的 **"项目管理"**
2. 在 "项目选择" 框中输入项目名称（如 "我的第一本小说"）
3. 点击 **"新建项目"** 按钮
4. （可选）上传相关资料文件：
   - 角色设定文档
   - 世界观设定
   - 大纲草稿
   - 参考资料

### 生成小说章节

1. 点击左侧导航栏的 **"写作生成"**
2. 选择刚创建的项目
3. 在 "生成要求" 中描述您的需求，例如：
   ```
   玄幻小说，主角是一个修仙者，性格冷静理智
   ```
4. 在 "大纲描述" 中输入章节大纲，例如：
   ```
   第一章：觉醒
   - 主角在村子里发现自己拥有特殊能力
   - 遇到神秘老者，获得修炼功法
   - 踏上修仙之路
   ```
5. 在右侧选择模型（如 deepseek-chat）
6. 点击 **"自动生成大纲"** 或 **"自动生成章节"**
7. 等待生成完成，查看和编辑结果

### 调整模型参数

- **Temperature (0.0-1.0)**: 控制创作随机性
  - 0.3 = 更保守、逻辑性强
  - 0.7 = 更有创意、多样性高
- **最大生成字数**: 控制章节长度（建议 3000-6000）

---

## 🛠️ 日常管理

### 启动/停止服务

| 操作 | 方式 |
|------|------|
| 启动服务 | 双击 `deploy.bat` |
| 停止服务 | 双击 `stop.bat` |
| 重启服务 | 双击 `restart.bat` |
| 查看日志 | 双击 `logs.bat` |

### 访问应用

在浏览器中访问：`http://localhost:8501`

### 数据备份

所有重要数据都保存在 `data` 目录：

```batch
# 创建备份（在项目目录打开命令行）
xcopy /E /I data data_backup_%date:~0,10%
```

建议定期备份该目录。

---

## 🔧 常见问题

### 1. Docker Desktop 无法启动

**问题**：提示 "WSL 2 未安装" 或类似错误

**解决**：
1. 访问 https://docs.microsoft.com/zh-cn/windows/wsl/install
2. 打开 PowerShell（管理员）
3. 运行：`wsl --install`
4. 重启电脑

### 2. 端口 8501 被占用

**现象**：部署失败，提示端口冲突

**解决**：
1. 打开 `docker-compose.yml`
2. 修改端口映射：
   ```yaml
   ports:
     - "8502:8501"  # 改用 8502 端口
   ```
3. 重新运行 `deploy.bat`
4. 访问 `http://localhost:8502`

### 3. 生成速度很慢

**原因**：可能是网络问题或 API 限流

**解决**：
- 检查网络连接
- 尝试切换其他模型提供商
- 减少 "最大生成字数"

### 4. 生成内容质量不佳

**建议**：
- 提供更详细的 "生成要求" 和 "大纲描述"
- 上传更多参考资料到知识库
- 调高 Temperature 参数（增加创意性）
- 尝试更强大的模型（如 GPT-4）

### 5. 查看详细错误日志

```batch
# 双击运行 logs.bat
# 或在命令行中运行：
docker compose logs -f
```

---

## 🔐 安全建议

1. **保护 API 密钥**
   - 不要分享 `.env` 文件
   - 定期更换 API 密钥
   - 设置 API 使用配额

2. **网络安全**
   - 默认仅本地访问（127.0.0.1）
   - 如需外网访问，请配置防火墙和 HTTPS

3. **数据安全**
   - 定期备份 `data` 目录
   - 不要删除正在运行的数据库文件

---

## 📊 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核 | 4 核或更高 |
| 内存 | 4GB | 8GB 或更高 |
| 磁盘 | 10GB | 50GB 或更高（含数据） |
| 网络 | 稳定的互联网连接 | 高速网络 |

---

## 🆘 技术支持

如遇到问题，请提供以下信息：

1. **错误截图**
2. **日志内容**（运行 `logs.bat` 获取）
3. **操作步骤**
4. **系统环境**（Windows 版本、Docker 版本）

联系方式：**ersonlzy@qq.com**

---

## 📝 更新说明

### 更新应用

当收到新版本部署包时：

```batch
# 1. 停止当前服务
stop.bat

# 2. 备份数据（重要！）
xcopy /E /I data data_backup

# 3. 解压新版本，覆盖所有文件（保留 .env 和 data 目录）

# 4. 重新部署
deploy.bat
```

---

## 📄 许可证

本软件仅供授权客户使用。未经授权，禁止复制、分发或二次开发。

---

## 🎉 开始创作

一切准备就绪！现在您可以：

1. 📝 创建您的小说项目
2. 🤖 让 AI 帮助您生成大纲和章节
3. ✨ 享受 AI 辅助写作的乐趣

祝您创作愉快！✍️
