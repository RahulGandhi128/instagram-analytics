@echo off
echo 🚀 Starting Instagram Analytics Application...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file and add your OpenAI API key, then run this script again.
    pause
    exit /b 1
)

REM Check if OPENAI_API_KEY is set
findstr "your_openai_api_key_here" .env >nul
if not errorlevel 1 (
    echo ⚠️  Please set your OPENAI_API_KEY in the .env file
    echo 📝 Edit .env and replace 'your_openai_api_key_here' with your actual OpenAI API key
    pause
    exit /b 1
)

REM Build and start the application
echo 🔨 Building and starting containers...
docker-compose up --build -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are healthy
echo 🔍 Checking service health...

REM Check backend
curl -f http://localhost:5000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Backend is healthy
) else (
    echo ❌ Backend health check failed
)

REM Check frontend
curl -f http://localhost:3000 >nul 2>&1
if not errorlevel 1 (
    echo ✅ Frontend is healthy
) else (
    echo ❌ Frontend health check failed
)

echo.
echo 🎉 Application is starting!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:5000
echo 💊 Health Check: http://localhost:5000/health
echo.
echo 📋 Useful commands:
echo   View logs: docker-compose logs -f
echo   Stop app: docker-compose down
echo   Restart: docker-compose restart
echo.
pause
