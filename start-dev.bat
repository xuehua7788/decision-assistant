@echo off
chcp 65001 >nul
color 0A

echo.
echo ========================================
echo   Decision Assistant - 开发环境启动
echo ========================================
echo.

echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装或未添加到 PATH
    echo 请安装 Python 3.8+ 并重试
    pause
    exit /b 1
)
python --version
echo ✅ Python 环境正常
echo.

echo [2/5] 检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装或未添加到 PATH
    echo 请安装 Node.js 14+ 并重试
    pause
    exit /b 1
)
node --version
npm --version
echo ✅ Node.js 环境正常
echo.

echo [3/5] 启动后端服务...
echo 正在安装后端依赖...
start "Decision-Backend" cmd /k "cd backend && echo 安装依赖... && pip install -r requirements.txt && echo. && echo ✅ 后端服务启动中... && echo. && uvicorn app.main:app --reload"
echo ⏳ 等待后端启动（10秒）...
timeout /t 10 /nobreak >nul
echo.

echo [4/5] 启动前端服务...
echo 正在安装前端依赖（首次较慢）...
start "Decision-Frontend" cmd /k "cd frontend && echo 安装依赖... && npm install && echo. && echo ✅ 前端服务启动中... && echo. && npm start"
echo ⏳ 等待前端启动（15秒）...
timeout /t 15 /nobreak >nul
echo.

echo [5/5] 打开浏览器...
timeout /t 5 /nobreak >nul
start http://localhost:3000
echo.

echo ========================================
echo   ✅ 所有服务已启动！
echo ========================================
echo.
echo 📍 访问地址:
echo   - 前端界面: http://localhost:3000
echo   - 后端 API: http://localhost:8000
echo   - API 文档: http://localhost:8000/docs
echo.
echo 💡 提示:
echo   - 后端窗口标题: Decision-Backend
echo   - 前端窗口标题: Decision-Frontend
echo   - 关闭对应窗口即可停止服务
echo.
echo 📚 文档:
echo   - 技术总结: 技术总结-第三方开发者.md
echo   - 集成指南: INTEGRATION_GUIDE.md
echo   - 快速启动: 快速启动指南.md
echo.
echo ========================================
echo.
echo 按任意键退出此窗口（不会关闭服务）...
pause >nul

