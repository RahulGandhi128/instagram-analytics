@echo off
echo Starting Instagram Analytics Development Environment...

echo.
echo Setting up Backend...
cd backend

echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo Starting Flask server...
start cmd /k "title Flask Server && python app.py"

echo.
echo Setting up Frontend...
cd ..\frontend

echo Installing Node dependencies...
if not exist "node_modules" (
    npm install
)

echo Starting React development server...
start cmd /k "title React Server && npm start"

cd ..

echo.
echo ================================
echo   Development Environment Ready
echo ================================
echo.
echo Backend (Flask): http://localhost:5000
echo Frontend (React): http://localhost:3000
echo.
echo Both servers are starting in separate windows...
echo Press any key to exit this setup script.

pause >nul
