@echo off
chcp 65001 >nul
title Nanban
cd /d "%~dp0"
set PYTHONUTF8=1

if not exist .venv\Scripts\python.exe (
    echo First time only: running setup...
    call setup.bat
    if not exist .venv\Scripts\python.exe exit /b 1
)

rem One click = lab + server + browser, all together.
.venv\Scripts\python.exe run_nanban.py
pause
