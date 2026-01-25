@echo off
chcp 65001 >nul
REM Novel Copilot - 客户部署包打包脚本 (Windows)
REM ========================================

echo.
echo ========================================
echo   Novel Copilot - 客户部署包打包
echo ========================================
echo.

REM 设置打包目录和输出文件名
set PACKAGE_NAME=novel-copilot-deployment
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set OUTPUT_FILE=%PACKAGE_NAME%-%TIMESTAMP%.zip

echo [1/4] 准备打包环境...

REM 检查是否安装了 PowerShell（用于压缩）
where powershell >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 PowerShell，无法创建 ZIP 文件
    pause
    exit /b 1
)

echo [√] PowerShell 已就绪

echo.
echo [2/4] 收集需要打包的文件...

REM 创建临时目录
set TEMP_DIR=temp_package_%RANDOM%
if exist "%TEMP_DIR%" rmdir /S /Q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

REM 复制必要的文件和目录
echo 复制源代码...
xcopy /E /I /Q app "%TEMP_DIR%\app\" >nul
xcopy /E /I /Q core "%TEMP_DIR%\core\" >nul
xcopy /E /I /Q llm "%TEMP_DIR%\llm\" >nul
xcopy /E /I /Q rag "%TEMP_DIR%\rag\" >nul
xcopy /E /I /Q config "%TEMP_DIR%\config\" >nul
xcopy /E /I /Q utils "%TEMP_DIR%\utils\" >nul
xcopy /E /I /Q pages "%TEMP_DIR%\pages\" >nul

echo 复制配置文件...
copy main.py "%TEMP_DIR%\" >nul
copy pyproject.toml "%TEMP_DIR%\" >nul
copy uv.lock "%TEMP_DIR%\" >nul
copy requirements.txt "%TEMP_DIR%\" >nul
copy .env.example "%TEMP_DIR%\" >nul
copy .python-version "%TEMP_DIR%\" >nul

echo 复制 Docker 配置...
copy Dockerfile "%TEMP_DIR%\" >nul
copy docker-compose.yml "%TEMP_DIR%\" >nul
copy .dockerignore "%TEMP_DIR%\" >nul

echo 复制部署脚本...
copy deploy.bat "%TEMP_DIR%\" >nul
copy stop.bat "%TEMP_DIR%\" >nul
copy restart.bat "%TEMP_DIR%\" >nul
copy logs.bat "%TEMP_DIR%\" >nul

echo 复制文档...
copy README.md "%TEMP_DIR%\" >nul
copy DOCKER_DEPLOYMENT.md "%TEMP_DIR%\" >nul

REM 创建空的数据目录结构
mkdir "%TEMP_DIR%\data"
mkdir "%TEMP_DIR%\data\db"
mkdir "%TEMP_DIR%\data\vectordb"
mkdir "%TEMP_DIR%\data\files"

REM 创建 .gitkeep 文件以保留空目录
echo. > "%TEMP_DIR%\data\db\.gitkeep"
echo. > "%TEMP_DIR%\data\vectordb\.gitkeep"
echo. > "%TEMP_DIR%\data\files\.gitkeep"

echo [√] 文件收集完成

echo.
echo [3/4] 创建 ZIP 压缩包...

REM 使用 PowerShell 压缩
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%OUTPUT_FILE%' -Force"
if errorlevel 1 (
    echo [错误] 创建 ZIP 文件失败
    rmdir /S /Q "%TEMP_DIR%"
    pause
    exit /b 1
)

echo [√] ZIP 文件创建成功: %OUTPUT_FILE%

echo.
echo [4/4] 清理临时文件...
rmdir /S /Q "%TEMP_DIR%"
echo [√] 清理完成

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 输出文件: %OUTPUT_FILE%
echo 文件大小: 
for %%A in ("%OUTPUT_FILE%") do echo %%~zA 字节
echo.
echo 部署说明:
echo 1. 将 %OUTPUT_FILE% 发送给客户
echo 2. 客户解压后，编辑 .env.example 并重命名为 .env
echo 3. 客户双击运行 deploy.bat 完成部署
echo.
pause
