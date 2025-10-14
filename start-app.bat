@echo off
chcp 65001 >nul
echo Starting Decision Assistant...

echo.
echo [1/3] Checking configuration...
if not exist backend\.env (
    echo Creating backend .env file...
    copy .env backend\.env
)
if not exist frontend\.env (
    echo Creating frontend .env file...
    echo REACT_APP_API_URL=http://127.0.0.1:8000 > frontend\.env
)

echo.
echo [2/3] Starting backend service...
cd backend
start cmd /k ".\venv\Scripts\activate && python app.py"
timeout /t 5

echo.
echo [3/3] Starting frontend service...
cd ..\frontend
start cmd /k "npm start"

echo.
echo All services started!
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close...
pause > nul
