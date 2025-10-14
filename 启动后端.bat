@echo off
chcp 65001 >nul
echo ========================================
echo   启动后端服务（带认证功能）
echo ========================================
echo.

cd backend

echo [1/2] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [2/2] 启动后端服务...
echo.
echo 后端服务启动在: http://127.0.0.1:8000
echo.
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

python app.py

pause


