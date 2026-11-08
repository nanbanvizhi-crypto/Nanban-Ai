@echo off
REM Nanban auto-start: launches Nanban (web app + Kali desktop warm-up) on Windows login.
cd /d "%~dp0"
set PYTHONUTF8=1
set OLLAMA_MODELS=D:\ollama\Nanban\ollama\models
".venv\Scripts\python.exe" run_nanban.py > "%LOCALAPPDATA%\Temp\nanban_startup.log" 2>&1
