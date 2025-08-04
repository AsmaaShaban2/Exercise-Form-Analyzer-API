@echo off
echo === Exercise Analysis API Docker Runner ===

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [INFO] Docker is running. Starting the application...

REM Create directories if they don't exist
if not exist uploads mkdir uploads
if not exist reports mkdir reports
if not exist logs mkdir logs

REM Build and run using docker-compose
docker-compose up --build

echo.
echo [INFO] Application stopped.
pause
