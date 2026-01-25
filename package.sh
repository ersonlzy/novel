#!/bin/bash
# Novel Copilot - 客户部署包打包脚本 (Mac/Linux)
# ========================================

echo ""
echo "========================================"
echo "  Novel Copilot - 客户部署包打包"
echo "========================================"
echo ""

# 设置打包目录和输出文件名
PACKAGE_NAME="novel-copilot-deployment"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${PACKAGE_NAME}-${TIMESTAMP}.zip"

echo "[1/4] 准备打包环境..."

# 检查是否安装了 zip 命令
if ! command -v zip &> /dev/null; then
    echo "[错误] 未找到 zip 命令，请先安装"
    echo "macOS: brew install zip"
    echo "Ubuntu: sudo apt-get install zip"
    exit 1
fi

echo "[√] zip 工具已就绪"

echo ""
echo "[2/4] 收集需要打包的文件..."

# 创建临时目录
TEMP_DIR="temp_package_$$"
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi
mkdir -p "$TEMP_DIR"

# 复制必要的文件和目录
echo "复制源代码..."
cp -r app "$TEMP_DIR/" 2>/dev/null || true
cp -r core "$TEMP_DIR/" 2>/dev/null || true
cp -r llm "$TEMP_DIR/" 2>/dev/null || true
cp -r rag "$TEMP_DIR/" 2>/dev/null || true
cp -r config "$TEMP_DIR/" 2>/dev/null || true
cp -r utils "$TEMP_DIR/" 2>/dev/null || true
cp -r pages "$TEMP_DIR/" 2>/dev/null || true

echo "复制配置文件..."
cp main.py "$TEMP_DIR/" 2>/dev/null || true
cp pyproject.toml "$TEMP_DIR/" 2>/dev/null || true
cp uv.lock "$TEMP_DIR/" 2>/dev/null || true
cp requirements.txt "$TEMP_DIR/" 2>/dev/null || true
cp .env.example "$TEMP_DIR/" 2>/dev/null || true
cp .python-version "$TEMP_DIR/" 2>/dev/null || true

echo "复制 Docker 配置..."
cp Dockerfile "$TEMP_DIR/" 2>/dev/null || true
cp docker-compose.yml "$TEMP_DIR/" 2>/dev/null || true
cp .dockerignore "$TEMP_DIR/" 2>/dev/null || true

echo "复制部署脚本..."
cp deploy.bat "$TEMP_DIR/" 2>/dev/null || true
cp stop.bat "$TEMP_DIR/" 2>/dev/null || true
cp restart.bat "$TEMP_DIR/" 2>/dev/null || true
cp logs.bat "$TEMP_DIR/" 2>/dev/null || true

echo "复制文档..."
cp README.md "$TEMP_DIR/" 2>/dev/null || true
cp DOCKER_DEPLOYMENT.md "$TEMP_DIR/" 2>/dev/null || true

# 创建空的数据目录结构
mkdir -p "$TEMP_DIR/data/db"
mkdir -p "$TEMP_DIR/data/vectordb"
mkdir -p "$TEMP_DIR/data/files"

# 创建 .gitkeep 文件以保留空目录
touch "$TEMP_DIR/data/db/.gitkeep"
touch "$TEMP_DIR/data/vectordb/.gitkeep"
touch "$TEMP_DIR/data/files/.gitkeep"

# 清理 Python 缓存文件
find "$TEMP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$TEMP_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$TEMP_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$TEMP_DIR" -type f -name ".DS_Store" -delete 2>/dev/null || true

echo "[√] 文件收集完成"

echo ""
echo "[3/4] 创建 ZIP 压缩包..."

# 创建 ZIP 文件
cd "$TEMP_DIR"
zip -r "../$OUTPUT_FILE" . -q
cd ..

if [ $? -eq 0 ]; then
    echo "[√] ZIP 文件创建成功: $OUTPUT_FILE"
else
    echo "[错误] 创建 ZIP 文件失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo ""
echo "[4/4] 清理临时文件..."
rm -rf "$TEMP_DIR"
echo "[√] 清理完成"

echo ""
echo "========================================"
echo "  打包完成！"
echo "========================================"
echo ""
echo "输出文件: $OUTPUT_FILE"
FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
echo "文件大小: $FILE_SIZE"
echo ""
echo "部署说明:"
echo "1. 将 $OUTPUT_FILE 发送给客户"
echo "2. 客户解压后，编辑 .env.example 并重命名为 .env"
echo "3. 客户双击运行 deploy.bat 完成部署（Windows）"
echo ""
