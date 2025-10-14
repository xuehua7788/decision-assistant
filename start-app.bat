@echo off
chcp 65001 >nul
echo ====================================
echo Starting Decision Assistant
echo ====================================
echo.

:: Check if dependencies are installed
if not exist backend\venv (
    echo Error: Backend not installed. Please run install.bat first
    pause
    exit /b 1
)

if not exist frontend\node_modules (
    echo Error: Frontend not installed. Please run install.bat first
    pause
    exit /b 1
)

:: Check environment files
if not exist backend\.env (
    echo Warning: backend\.env not found
    echo Please create backend\.env with your OpenAI API key
)

if not exist frontend\.env (
    echo Creating frontend\.env...
    echo REACT_APP_API_URL=http://127.0.0.1:8000 > frontend\.env
)

echo.
echo [1/2] Starting backend server...
cd backend
start cmd /k ".\venv\Scripts\activate && python app.py"
cd ..
timeout /t 5 /nobreak > nul

echo.
echo [2/2] Starting frontend server...
cd frontend
start cmd /k "npm start"
cd ..

echo.
echo ====================================
echo Application is starting...
echo ====================================
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
