@echo off
REM Docker build and run script for Exercise Analysis API (Windows)

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=exercise-analysis-api
set CONTAINER_NAME=exercise-analysis-container
set PORT=5000

echo === Exercise Analysis API Docker Build Script ===
echo.

REM Check if Docker is installed and running
:check_docker
echo [INFO] Checking Docker installation...

docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker first.
    exit /b 1
)

echo [INFO] Docker is installed and running.
goto main

REM Build Docker image
:build_image
echo [INFO] Building Docker image: %IMAGE_NAME%

REM Check if image exists and remove it
docker image inspect %IMAGE_NAME% >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Removing existing image: %IMAGE_NAME%
    docker rmi %IMAGE_NAME%
)

REM Build the image
docker build -t %IMAGE_NAME% .

if errorlevel 1 (
    echo [ERROR] Failed to build Docker image.
    exit /b 1
)

echo [INFO] Docker image built successfully!
goto :eof

REM Stop and remove existing container
:cleanup_container
docker ps -a --format "table {{.Names}}" | findstr /r "^%CONTAINER_NAME%$" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Stopping and removing existing container: %CONTAINER_NAME%
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
)
goto :eof

REM Run Docker container
:run_container
echo [INFO] Starting Docker container: %CONTAINER_NAME%

REM Create necessary directories on host
if not exist uploads mkdir uploads
if not exist reports mkdir reports
if not exist logs mkdir logs

REM Run the container
docker run -d ^
    --name %CONTAINER_NAME% ^
    -p %PORT%:5000 ^
    -v "%cd%/uploads:/app/uploads" ^
    -v "%cd%/reports:/app/reports" ^
    -v "%cd%/logs:/app/logs" ^
    -e FLASK_ENV=production ^
    %IMAGE_NAME%

if errorlevel 1 (
    echo [ERROR] Failed to start container.
    exit /b 1
)

echo [INFO] Container started successfully!
echo [INFO] API is available at: http://localhost:%PORT%
echo [INFO] Health check: http://localhost:%PORT%/health
goto :eof

REM Show container logs
:show_logs
echo [INFO] Container logs:
docker logs %CONTAINER_NAME%
goto :eof

REM Show container status
:show_status
echo [INFO] Container status:
docker ps --filter "name=%CONTAINER_NAME%"
goto :eof

REM Clean up containers and images
:clean
echo [INFO] Cleaning up containers and images...
call :cleanup_container
docker image inspect %IMAGE_NAME% >nul 2>&1
if not errorlevel 1 (
    docker rmi %IMAGE_NAME%
)
echo [INFO] Cleanup complete.
goto :eof

REM Show help
:show_help
echo Usage: %0 [command]
echo.
echo Commands:
echo   build         Build Docker image only
echo   run           Run container (assumes image exists)
echo   build-and-run Build image and run container (default)
echo   stop          Stop running container
echo   logs          Show container logs
echo   status        Show container status
echo   clean         Remove container and image
echo   help          Show this help message
goto :eof

REM Main execution
:main
if "%1"=="" goto build_and_run
if "%1"=="build" goto build_only
if "%1"=="run" goto run_only
if "%1"=="build-and-run" goto build_and_run
if "%1"=="stop" goto stop_container
if "%1"=="logs" goto show_logs
if "%1"=="status" goto show_status
if "%1"=="clean" goto clean
if "%1"=="help" goto show_help

echo [ERROR] Unknown command: %1
echo Use '%0 help' for usage information.
exit /b 1

:build_only
call :build_image
goto end

:run_only
call :cleanup_container
call :run_container
goto end

:build_and_run
call :build_image
call :cleanup_container
call :run_container
goto end

:stop_container
echo [INFO] Stopping container: %CONTAINER_NAME%
docker stop %CONTAINER_NAME%
goto end

:end
echo.
echo Script completed.
pause
