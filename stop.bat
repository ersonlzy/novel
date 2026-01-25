@echo off
chcp 65001 >nul
REM Novel Copilot - 停止服务脚本
REM ========================================

echo.
echo ========================================
echo   停止 Novel Copilot 服务
echo ========================================
echo.

docker compose stop
if errorlevel 1 (
    echo [错误] 停止服务失败
    pause
    exit /b 1
)

echo.
echo [√] 服务已停止
echo.
pause
