@echo off
chcp 65001 >nul
echo ========================================
echo   启动前端服务
echo ========================================
echo.

cd frontend

echo 前端服务启动在: http://localhost:3000
echo.
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

npm start

pause


