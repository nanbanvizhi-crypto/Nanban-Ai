@echo off
chcp 65001 >nul
title Nanban Terminal
set PYTHONUTF8=1

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Please run setup.bat first.
    pause
    exit /b 1
)

rem Opens in your home folder. Type `nanban` in any folder to open it there instead.
cd /d "%USERPROFILE%"
"%~dp0.venv\Scripts\python.exe" "%~dp0terminal.py"
