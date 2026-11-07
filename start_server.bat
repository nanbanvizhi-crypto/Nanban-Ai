@echo off
chcp 65001 >nul
title Nanban Server
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist .venv\Scripts\python.exe (
    echo Please run setup.bat first.
    pause
    exit /b 1
)
.venv\Scripts\python.exe server.py %*
pause
