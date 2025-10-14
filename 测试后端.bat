@echo off
chcp 65001 >nul
echo 测试后端API...
echo.

echo [1] 测试健康检查:
curl -s http://127.0.0.1:8000/health
echo.
echo.

echo [2] 测试注册API:
curl -X POST http://127.0.0.1:8000/api/auth/register -H "Content-Type: application/json" -d "{\"username\":\"test123\",\"password\":\"123456\"}"
echo.
echo.

pause

