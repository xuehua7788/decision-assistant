@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo 📝 查看具体会话内容
echo ================================================================================
echo.

if "%1"=="" (
    echo ❌ 请提供会话ID！
    echo.
    echo 使用方法:
    echo   1. 先运行 查看聊天记录.bat 获取会话ID列表
    echo   2. 然后运行: 查看具体会话.bat [会话ID]
    echo.
    echo 示例:
    echo   查看具体会话.bat test
    echo   查看具体会话.bat 4e37bb85-c3a6-4eaf-9ec7-b81ce6ca5d5f
    echo.
    pause
    exit /b 1
)

python quick_view_chat.py %1

echo.
pause

