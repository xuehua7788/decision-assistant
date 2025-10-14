@echo off
echo ====================================
echo Installing Decision Assistant
echo ====================================

echo.
echo [1/4] Installing backend dependencies...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo [2/4] Installing frontend dependencies...
cd ../frontend
call npm install

echo.
echo [3/4] Setting up environment files...
cd ..
if not exist frontend\.env (
    echo Creating frontend\.env...
    echo REACT_APP_API_URL=http://127.0.0.1:8000 > frontend\.env
)

if not exist backend\.env (
    echo Creating backend\.env...
    echo OPENAI_API_KEY=sk-d3196d84dbb3408eb3ac946da3f8d4ba > backend\.env
)

echo.
echo ====================================
echo Installation complete!
echo ====================================
echo.
echo To start the application, run: start-app.bat
pause
