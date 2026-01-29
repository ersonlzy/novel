@echo off
chcp 65001 >nul
REM Novel Copilot - Windows 一键部署脚本
REM ========================================

echo.
echo ========================================
echo   Novel Copilot - Docker 一键部署
echo ========================================
echo.

REM 检查 Docker 是否安装
echo [1/6] 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop for Windows
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [√] Docker 已安装

REM 检查 Docker Compose 是否可用
docker compose version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker Compose 不可用，请确保 Docker Desktop 正在运行
    pause
    exit /b 1
)
echo [√] Docker Compose 已就绪

REM 创建必要的数据目录
echo.
echo [2/6] 创建数据目录...
if not exist "data\db" mkdir "data\db"
if not exist "data\vectordb" mkdir "data\vectordb"
if not exist "data\files" mkdir "data\files"
echo [√] 数据目录创建完成

REM 检查 .env 文件
echo.
echo [3/6] 检查环境配置...
if exist ".env\" (
    echo [!] 检测到 .env 是一个文件夹（可能是 Docker 错误创建的）
    echo [!] 正在删除该文件夹并从 .env.example 重新创建...
    rmdir /s /q ".env"
    copy ".env.example" ".env" >nul
)

if not exist ".env" (
    echo [!] 未找到 .env 文件，从 .env.example 复制...
    copy ".env.example" ".env" >nul
    echo [!] 请编辑 .env 文件，配置您的 API Keys
    echo.
    set /p CONTINUE="是否继续部署？(Y/N): "
    if /i not "%CONTINUE%"=="Y" (
        echo 部署已取消
        pause
        exit /b 0
    )
) else (
    echo [√] .env 文件已存在
)

REM 停止并删除旧容器（如果存在）
echo.
echo [4/6] 清理旧容器...
echo [4/6] 清理旧容器和镜像...
docker compose down --rmi local >nul 2>&1
echo [√] 旧容器已清理

REM 构建并启动服务
echo.
echo [5/6] 构建 Docker 镜像...
docker compose build --no-cache
if errorlevel 1 (
    echo [错误] Docker 镜像构建失败
    pause
    exit /b 1
)
echo [√] Docker 镜像构建完成

echo.
echo [6/6] 启动服务...
docker compose up -d
if errorlevel 1 (
    echo [错误] 服务启动失败
    pause
    exit /b 1
)

REM 等待服务启动
echo.
echo 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
docker compose ps
echo.
echo 访问地址: http://localhost:8501
echo.
echo 常用命令:
echo   查看日志: docker compose logs -f
echo   停止服务: docker compose stop
echo   启动服务: docker compose start
echo   重启服务: docker compose restart
echo   完全删除: docker compose down
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:8501
