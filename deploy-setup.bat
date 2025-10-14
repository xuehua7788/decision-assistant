@echo off
REM Decision Assistant 一键部署配置脚本 (Windows)
REM 使用方法: 直接双击运行或在命令行中执行 deploy-setup.bat

setlocal enabledelayedexpansion

echo ==========================================
echo Decision Assistant 部署配置向导
echo ==========================================
echo.

REM 检查必要工具
echo 检查必要工具...

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未安装 Git
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未安装 Node.js
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未安装 npm
    pause
    exit /b 1
)

echo [OK] 工具检查完成
echo.

REM 选择部署方案
echo 请选择部署方案:
echo 1) Vercel + Render (免费，推荐新手)
echo 2) Vercel + Railway (付费，稳定)
echo 3) Cloudflare Pages + Fly.io (高性价比)
echo 4) 仅本地测试
echo.

set /p deployment_choice="请输入选项 (1-4): "

if "%deployment_choice%"=="1" (
    set PLATFORM_FRONTEND=vercel
    set PLATFORM_BACKEND=render
) else if "%deployment_choice%"=="2" (
    set PLATFORM_FRONTEND=vercel
    set PLATFORM_BACKEND=railway
) else if "%deployment_choice%"=="3" (
    set PLATFORM_FRONTEND=cloudflare
    set PLATFORM_BACKEND=flyio
) else if "%deployment_choice%"=="4" (
    set PLATFORM_FRONTEND=local
    set PLATFORM_BACKEND=local
) else (
    echo [错误] 无效选项
    pause
    exit /b 1
)

echo [OK] 选择: 前端=%PLATFORM_FRONTEND%, 后端=%PLATFORM_BACKEND%
echo.

REM 收集环境变量
echo ==========================================
echo 环境变量配置
echo ==========================================
echo.

set /p DEEPSEEK_KEY="请输入 DeepSeek API Key (sk-...): "

if not "%PLATFORM_BACKEND%"=="local" (
    set /p BACKEND_URL="后端部署完成后的 URL (留空则稍后配置): "
) else (
    set BACKEND_URL=http://localhost:8000
)

if not "%PLATFORM_FRONTEND%"=="local" (
    set /p FRONTEND_URL="前端部署完成后的 URL (留空则稍后配置): "
) else (
    set FRONTEND_URL=http://localhost:3000
)

echo.
echo [OK] 环境变量收集完成
echo.

REM 创建环境变量文件
echo 创建环境变量文件...

REM 后端 .env
(
echo # DeepSeek API Configuration
echo DEEPSEEK_API_KEY=%DEEPSEEK_KEY%
echo.
echo # CORS Configuration
echo ALLOWED_ORIGINS=["%FRONTEND_URL%","http://localhost:3000"]
echo.
echo # Chat Storage
echo CHAT_STORAGE_DIR=chat_data
echo MAX_HISTORY_MESSAGES=20
) > backend\.env

echo [OK] 创建 backend\.env

REM 前端 .env
(
echo # Backend API URL
echo REACT_APP_API_URL=%BACKEND_URL%
) > frontend\.env

echo [OK] 创建 frontend\.env

REM .env.example
(
echo DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
echo ALLOWED_ORIGINS=["http://localhost:3000","https://your-frontend-domain.com"]
echo CHAT_STORAGE_DIR=chat_data
echo MAX_HISTORY_MESSAGES=20
) > backend\.env.example

(
echo REACT_APP_API_URL=http://localhost:8000
) > frontend\.env.example

echo.

REM 安装依赖
echo ==========================================
echo 安装依赖
echo ==========================================
echo.

echo 安装前端依赖...
cd frontend
call npm install
cd ..
echo [OK] 前端依赖安装完成
echo.

echo 安装后端依赖...
cd backend
python -m pip install -r requirements.txt
cd ..
echo [OK] 后端依赖安装完成
echo.

REM 创建启动脚本
echo 创建启动脚本...

REM 本地启动脚本
(
echo @echo off
echo echo 启动 Decision Assistant...
echo.
echo echo 启动后端...
echo start "Backend" cmd /k "cd backend && uvicorn app.main:app --reload"
echo.
echo timeout /t 3 /nobreak ^>nul
echo.
echo echo 启动前端...
echo start "Frontend" cmd /k "cd frontend && npm start"
echo.
echo echo.
echo echo 后端运行在: http://localhost:8000
echo echo 前端运行在: http://localhost:3000
echo echo.
echo echo 按任意键关闭此窗口
echo pause ^>nul
) > start-local.bat

echo [OK] 创建 start-local.bat

REM 测试脚本
(
echo @echo off
echo echo 测试部署...
echo echo.
echo.
echo echo 测试后端健康检查...
echo curl -s "%BACKEND_URL%/health"
echo echo.
echo.
echo echo 测试前端...
echo curl -s -o nul -w "HTTP Status: %%{http_code}" "%FRONTEND_URL%"
echo echo.
echo echo.
echo echo 测试完成
echo pause
) > test-deployment.bat

echo [OK] 创建 test-deployment.bat
echo.

REM 生成部署报告
(
echo # 部署信息
echo.
echo **部署日期:** %date% %time%
echo **方案:** 前端=%PLATFORM_FRONTEND%, 后端=%PLATFORM_BACKEND%
echo.
echo ## 环境变量
echo.
echo ### 后端
echo ```
echo DEEPSEEK_API_KEY=%DEEPSEEK_KEY:~0,10%...
echo ALLOWED_ORIGINS=["%FRONTEND_URL%"]
echo ```
echo.
echo ### 前端
echo ```
echo REACT_APP_API_URL=%BACKEND_URL%
echo ```
echo.
echo ## URL
echo.
echo - 前端: %FRONTEND_URL%
echo - 后端: %BACKEND_URL%
echo.
echo ## 下一步
echo.
echo 1. 部署后端到 %PLATFORM_BACKEND%
echo 2. 部署前端到 %PLATFORM_FRONTEND%
echo 3. 运行测试: test-deployment.bat
echo.
echo ## 文档
echo.
echo - [部署方案完整指南](部署方案完整指南.md^)
echo - [部署快速检查](部署快速检查.md^)
) > DEPLOYMENT_INFO.md

echo [OK] 生成部署报告: DEPLOYMENT_INFO.md
echo.

REM 部署指引
echo ==========================================
echo 部署指引
echo ==========================================
echo.

if "%PLATFORM_BACKEND%"=="render" (
    echo 后端部署到 Render:
    echo 1. 访问 https://render.com
    echo 2. 点击 'New +' -^> 'Web Service'
    echo 3. 连接您的 GitHub 仓库
    echo 4. 配置:
    echo    - Root Directory: backend
    echo    - Build Command: pip install -r requirements.txt
    echo    - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    echo 5. 环境变量:
    echo    - DEEPSEEK_API_KEY=%DEEPSEEK_KEY%
    echo.
)

if "%PLATFORM_BACKEND%"=="railway" (
    echo 后端部署到 Railway:
    echo 1. 访问 https://railway.app
    echo 2. 导入 GitHub 仓库
    echo 3. 选择 'backend' 目录
    echo 4. 环境变量:
    echo    - DEEPSEEK_API_KEY=%DEEPSEEK_KEY%
    echo    - PORT=8000
    echo.
)

if "%PLATFORM_FRONTEND%"=="vercel" (
    echo 前端部署到 Vercel:
    echo 运行以下命令:
    echo   npm install -g vercel
    echo   cd frontend
    echo   vercel login
    echo   vercel --prod
    echo.
    echo 或访问 https://vercel.com 使用 GitHub 集成
    echo.
)

if "%PLATFORM_FRONTEND%"=="local" (
    if "%PLATFORM_BACKEND%"=="local" (
        echo 本地运行:
        echo   双击运行 start-local.bat
        echo.
        echo 或在命令行中运行:
        echo   start-local.bat
        echo.
    )
)

echo ==========================================
echo [OK] 配置完成！
echo ==========================================
echo.
echo 下一步:
echo 1. 查看部署信息: type DEPLOYMENT_INFO.md
echo 2. 查看详细指南: start 部署方案完整指南.md
echo.

if "%PLATFORM_FRONTEND%"=="local" (
    if "%PLATFORM_BACKEND%"=="local" (
        echo 本地运行:
        echo   start-local.bat
        echo.
    )
) else (
    echo 开始部署:
    echo   按照上面的部署指引操作
    echo.
)

echo 祝部署顺利！
echo.
pause

