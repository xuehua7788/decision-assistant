@echo off
REM 用户画像系统测试脚本（Windows）

echo ======================================================================
echo 用户画像系统测试
echo ======================================================================
echo.

REM 设置环境变量（请替换为你的实际值）
echo 1. 设置环境变量...
set DATABASE_URL=postgresql://decision_user:YOUR_PASSWORD@dpg-d3otin3ipnbc739gk7g-a.singapore-postgres.render.com:5432/decision_assistant_0981
set DEEPSEEK_API_KEY=YOUR_DEEPSEEK_KEY
set USE_DATABASE=true
set ENABLE_USER_PROFILING=true

echo    DATABASE_URL: 已设置
echo    DEEPSEEK_API_KEY: 已设置
echo.

REM 创建数据库表
echo 2. 创建数据库表...
python create_user_profile_tables.py
if %errorlevel% neq 0 (
    echo    ❌ 数据库表创建失败
    pause
    exit /b 1
)
echo.

REM 运行测试
echo 3. 运行系统测试...
python test_profile_system.py
echo.

echo ======================================================================
echo 测试完成
echo ======================================================================
pause

