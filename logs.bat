@echo off
chcp 65001 >nul
REM Novel Copilot - 查看日志脚本
REM ========================================

echo.
echo ========================================
echo   Novel Copilot 实时日志
echo   按 Ctrl+C 退出
echo ========================================
echo.

docker compose logs -f
