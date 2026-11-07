@echo off
chcp 65001 >nul
title Nanban Security Lab
cd /d "%~dp0"

echo.
echo ============================================
echo    Nanban Security Lab  -  local practice only
echo ============================================
echo.

docker --version >nul 2>nul
if errorlevel 1 (
    echo [X] Docker is not installed.
    echo     Install Docker Desktop from https://www.docker.com/products/docker-desktop/
    echo     Open it once so it is running, then run start_lab.bat again.
    pause
    exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
    echo [X] Docker is installed but not running. Open Docker Desktop and wait for it to start.
    pause
    exit /b 1
)

echo Starting the practice targets (first time downloads a few GB)...
docker compose up -d
if errorlevel 1 (
    echo [X] Could not start the lab. Is Docker Desktop running?
    pause
    exit /b 1
)

echo.
echo ============================================
echo    Lab is running on THIS computer only:
echo.
echo    DVWA        http://127.0.0.1:8080   (login: admin / password)
   Mutillidae  http://127.0.0.1:8082   ^|  bWAPP  http://127.0.0.1:8083/install.php
   VAmPI(API)  http://127.0.0.1:5001    ^|  DVGA   http://127.0.0.1:5013
echo    Juice Shop  http://127.0.0.1:3000
echo    WebGoat     http://127.0.0.1:8081/WebGoat
echo.
echo    These are the ONLY systems you may attack.
echo    Stop the lab anytime with  stop_lab.bat
echo ============================================
start http://127.0.0.1:3000
pause
