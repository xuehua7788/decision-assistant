@echo off
chcp 65001 >nul
color 0B
echo.
echo ========================================
echo   Decision Assistant - 认证版本启动
echo ========================================
echo.

echo [1/4] 安装后端依赖...
cd backend
echo 正在安装认证相关依赖...
pip install passlib[bcrypt] python-jose[cryptography] sqlalchemy --quiet
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    echo 💡 尝试运行: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ 后端依赖安装完成
echo.

echo [2/4] 启动后端服务 (端口 8000)...
start "Decision-Backend-Auth" cmd /k "python app.py"
echo ⏳ 等待后端启动 (8秒)...
timeout /t 8 /nobreak >nul
cd ..
echo ✅ 后端服务已启动
echo.

echo [3/4] 测试后端 API...
python test-auth-api.py
echo.

echo [4/4] 启动前端服务 (端口 3000)...
cd frontend
start "Decision-Frontend" cmd /k "npm start"
echo ⏳ 等待前端启动 (10秒)...
timeout /t 10 /nobreak >nul
cd ..
echo ✅ 前端服务已启动
echo.

echo ========================================
echo   ✅ 所有服务已启动！
echo ========================================
echo.
echo 📍 访问地址:
echo   http://localhost:3000
echo.
echo 🔐 认证功能:
echo   - 用户注册: 创建新账户
echo   - 用户登录: 使用已有账户
echo   - 用户退出: 安全退出
echo.
echo 💾 数据存储:
echo   backend\users_data.json
echo.
echo 💡 提示:
echo   关闭对应窗口可停止服务
echo.

timeout /t 3 /nobreak >nul
start http://localhost:3000

echo 按任意键退出此窗口...
pause >nul


