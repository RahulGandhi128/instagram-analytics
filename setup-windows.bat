@echo off
echo ============================================
echo   Instagram Analytics - Windows Setup
echo ============================================

echo.
echo Step 1: Setting up Backend (Flask)...
cd backend

echo Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing core dependencies first...
pip install --upgrade pip

echo Installing minimal requirements for development...
pip install -r requirements-dev.txt

echo.
echo Testing Flask installation...
python -c "import flask; print('Flask version:', flask.__version__)"
if %errorlevel% neq 0 (
    echo ERROR: Flask installation failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up Frontend (React)...
cd ..\frontend

echo Installing Node.js dependencies...
if not exist "node_modules" (
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: npm install failed!
        pause
        exit /b 1
    )
) else (
    echo Node modules already installed.
)

echo.
echo Step 3: Testing the setup...
cd ..\backend
call venv\Scripts\activate

echo Testing database initialization...
python -c "
from models.database import db
from app import create_app
app = create_app()
with app.app_context():
    try:
        db.create_all()
        print('✅ Database tables created successfully!')
    except Exception as e:
        print('❌ Database error:', e)
"

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To start development servers:
echo.
echo Backend (Flask):
echo   cd backend
echo   venv\Scripts\activate
echo   python app.py
echo.
echo Frontend (React) - in another terminal:
echo   cd frontend  
echo   npm start
echo.
echo The app will be available at:
echo   Backend API: http://localhost:5000
echo   Frontend:    http://localhost:3000
echo.

echo Starting servers now? (y/n)
set /p start_servers="Enter choice: "

if /i "%start_servers%"=="y" (
    echo.
    echo Starting Flask server...
    start cmd /k "title Flask Server && cd backend && venv\Scripts\activate && python app.py"
    
    timeout /t 3 /nobreak >nul
    
    echo Starting React server...
    start cmd /k "title React Server && cd frontend && npm start"
    
    echo.
    echo Both servers are starting in separate windows...
    echo Check http://localhost:3000 in your browser in a few moments.
)

echo.
echo Setup script completed. Press any key to exit.
pause >nul
