@echo off
chcp 65001 >nul
REM Novel Copilot - 重启服务脚本
REM ========================================

echo.
echo ========================================
echo   重启 Novel Copilot 服务
echo ========================================
echo.

docker compose restart
if errorlevel 1 (
    echo [错误] 重启服务失败
    pause
    exit /b 1
)

echo.
echo [√] 服务已重启
echo.
echo 访问地址: http://localhost:8501
echo.
pause
