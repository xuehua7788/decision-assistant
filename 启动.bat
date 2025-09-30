@echo off
echo ======================================
echo   Decision Assistant 一???
echo ======================================
echo.
echo [1/2] ??后端服?...
start powershell -NoExit -Command "cd C:\Users\NP930\Desktop\decision-assistant && docker-compose -f docker-compose-backend.yml up"

echo [2/2] 等待5秒后??前端...
timeout /t 5 /nobreak > nul

start powershell -NoExit -Command "cd C:\Users\NP930\Desktop\decision-assistant\frontend && npm start"

echo.
echo ??完成！??器?自?打?...
echo.
echo ??方法：
echo 1. 在??黑窗口按 Ctrl+C
echo 2. 在Docker窗口?入: docker-compose -f docker-compose-backend.yml down
echo.
pause
