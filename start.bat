@echo off
chcp 65001 >nul
title Local AI Agent
cd /d "%~dp0"
set PYTHONUTF8=1

if not exist .venv\Scripts\activate.bat (
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python app.py
pause
