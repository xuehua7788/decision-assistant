@echo off
chcp 65001 >nul
color 0E
echo.
echo ========================================
echo   聊天记录查看器
echo ========================================
echo.

echo 📁 后端聊天记录（按用户名）:
echo.
if exist "backend\chat_data" (
    dir /b "backend\chat_data\*.json" 2>nul
    echo.
) else (
    echo ⚠️  后端聊天记录目录不存在
    echo.
)

if exist "chat_data" (
    echo 📁 根目录聊天记录:
    echo.
    dir /b "chat_data\*.json" 2>nul
    echo.
)

echo.
echo ========================================
echo 💡 查看某个文件的内容:
echo.
set /p filename="请输入文件名（如 admin.json）: "

if exist "backend\chat_data\%filename%" (
    echo.
    echo 📄 backend\chat_data\%filename%
    echo ----------------------------------------
    type "backend\chat_data\%filename%"
    echo.
    echo ----------------------------------------
) else if exist "chat_data\%filename%" (
    echo.
    echo 📄 chat_data\%filename%
    echo ----------------------------------------
    type "chat_data\%filename%"
    echo.
    echo ----------------------------------------
) else (
    echo.
    echo ❌ 文件不存在: %filename%
    echo.
)

echo.
echo ========================================
echo.
pause

