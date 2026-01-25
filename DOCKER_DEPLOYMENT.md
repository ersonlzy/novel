# Novel Copilot - Docker 部署指南

## 📋 前置要求

- **Windows 10/11** 64位系统
- **Docker Desktop for Windows** 
  - 下载地址: https://www.docker.com/products/docker-desktop
  - 安装后需要重启电脑
- 至少 **4GB** 可用内存
- 至少 **10GB** 可用磁盘空间

---

## 🚀 快速部署（推荐）

### 1. 配置环境变量

首次部署前，请编辑 `.env` 文件，配置您的 API Keys：

```bash
# 编辑 .env 文件，填入您的 API Keys
notepad .env
```

主要配置项：
```env
# OpenAI 配置
OPENAI_API_KEY=sk-your-api-key-here

# DeepSeek 配置
DEEPSEEK_API_KEY=sk-your-api-key-here

# 其他大模型配置...
```

### 2. 一键部署

双击运行 **`deploy.bat`** 文件，脚本会自动完成以下步骤：

1. ✅ 检查 Docker 环境
2. ✅ 创建数据目录
3. ✅ 检查环境配置
4. ✅ 清理旧容器
5. ✅ 构建 Docker 镜像
6. ✅ 启动服务

部署成功后，浏览器会自动打开 `http://localhost:8501`

---

## 📂 数据持久化

所有重要数据都会保存在以下目录，不会因为容器重启而丢失：

```
novel/
├── data/
│   ├── db/          # SQLite 数据库文件
│   ├── vectordb/    # 向量数据库文件
│   └── files/       # 用户上传的文件
└── .env             # 环境配置文件
```

### 数据备份

定期备份 `data` 目录即可：

```batch
REM 创建备份
xcopy /E /I data data_backup_%date:~0,10%
```

---

## 🛠️ 常用管理脚本

| 脚本文件 | 功能说明 |
|---------|---------|
| `deploy.bat` | 一键部署服务 |
| `stop.bat` | 停止服务 |
| `restart.bat` | 重启服务 |
| `logs.bat` | 查看实时日志 |

### 手动命令

```batch
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose stop

# 启动服务
docker compose start

# 重启服务
docker compose restart

# 完全删除容器和网络（数据保留）
docker compose down

# 重新构建镜像
docker compose build --no-cache

# 强制重新部署
docker compose down
docker compose up -d --build
```

---

## 🔧 故障排除

### 1. Docker Desktop 未启动

**错误**：`error during connect: This error may indicate that the docker daemon is not running`

**解决**：
1. 打开 Docker Desktop 应用
2. 等待 Docker 完全启动（右下角图标显示绿色）
3. 重新运行 `deploy.bat`

### 2. 端口被占用

**错误**：`Bind for 0.0.0.0:8501 failed: port is already allocated`

**解决**：
1. 修改 `docker-compose.yml` 中的端口映射：
   ```yaml
   ports:
     - "8502:8501"  # 改用 8502 端口
   ```
2. 或者找到占用 8501 端口的程序并关闭

### 3. 内存不足

**错误**：容器频繁重启或崩溃

**解决**：
1. 打开 Docker Desktop Settings
2. 进入 Resources → Advanced
3. 增加 Memory 限制到至少 4GB
4. 重启 Docker Desktop

### 4. 镜像构建失败

**解决**：
```batch
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker compose build --no-cache
```

### 5. 查看详细错误信息

```batch
# 查看容器日志
docker compose logs novel-copilot

# 进入容器调试
docker compose exec novel-copilot /bin/bash
```

---

## 🔐 安全建议

1. **不要将 `.env` 文件提交到 Git**：
   - `.env` 文件已在 `.gitignore` 中
   - 使用 `.env.example` 作为模板

2. **保护 API Keys**：
   - 定期轮换 API Keys
   - 使用只读权限的 API Keys（如果支持）

3. **网络访问控制**：
   ```yaml
   # 仅允许本地访问，修改 docker-compose.yml
   ports:
     - "127.0.0.1:8501:8501"  # 仅本机可访问
   ```

---

## 📊 性能优化

### 1. 使用国内镜像加速

在 Docker Desktop 中配置镜像加速器：

1. Settings → Docker Engine
2. 添加配置：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

### 2. 限制资源使用

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  novel-copilot:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G
```

---

## 🌐 外网访问配置

### 使用端口映射（仅测试环境）

```yaml
# docker-compose.yml
ports:
  - "0.0.0.0:8501:8501"  # 允许外网访问
```

⚠️ **警告**：不建议在生产环境直接暴露端口，建议使用反向代理（Nginx、Caddy）配合 HTTPS。

---

## 📝 更新应用

```batch
# 1. 拉取最新代码
git pull

# 2. 停止服务
docker compose down

# 3. 重新部署
deploy.bat
```

---

## 🗑️ 完全卸载

```batch
# 1. 删除容器和网络
docker compose down

# 2. 删除镜像
docker rmi novel-copilot

# 3. 删除数据（可选）
rmdir /S /Q data

# 4. 清理 Docker 系统
docker system prune -a
```

---

## 📞 技术支持

- **维护者**: ersonlzy@qq.com
- **问题反馈**: 请提交 GitHub Issue

---

## 📄 许可证

本项目遵循项目主许可证。
