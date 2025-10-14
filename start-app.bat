@echo off
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
    echo Error: backend\.env not found
    echo Please create backend\.env with your OpenAI API key
    pause
    exit /b 1
)

if not exist frontend\.env (
    echo Creating frontend\.env...
    echo REACT_APP_API_URL=http://127.0.0.1:8000 > frontend\.env
)

echo Starting backend server...
start cmd /k "cd backend && venv\Scripts\activate && python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting frontend server...
start cmd /k "cd frontend && npm start"

echo.
echo ====================================
echo Application is starting...
echo ====================================
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
