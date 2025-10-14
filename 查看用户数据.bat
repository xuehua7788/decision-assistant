@echo off
chcp 65001 >nul
color 0B
echo.
echo ========================================
echo   用户数据查看器
echo ========================================
echo.

if exist "backend\users_data.json" (
    echo 📄 backend\users_data.json
    echo ----------------------------------------
    type "backend\users_data.json"
    echo.
    echo ----------------------------------------
) else (
    echo ❌ 用户数据文件不存在
)

echo.
echo 💡 提示:
echo   - 密码已加密（hashed_password）
echo   - 用户名（username）
echo   - 账户状态（is_active）
echo.
pause

