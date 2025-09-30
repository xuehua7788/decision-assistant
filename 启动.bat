@echo off
echo ======================================
echo   Decision Assistant �@???
echo ======================================
echo.
echo [1/2] ??�Z�ݪA?...
start powershell -NoExit -Command "cd C:\Users\NP930\Desktop\decision-assistant && docker-compose -f docker-compose-backend.yml up"

echo [2/2] ����5��Z??�e��...
timeout /t 5 /nobreak > nul

start powershell -NoExit -Command "cd C:\Users\NP930\Desktop\decision-assistant\frontend && npm start"

echo.
echo ??�����I??��?��?��?...
echo.
echo ??��k�G
echo 1. �b??�µ��f�� Ctrl+C
echo 2. �bDocker���f?�J: docker-compose -f docker-compose-backend.yml down
echo.
pause
