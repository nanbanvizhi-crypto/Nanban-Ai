@echo off
cd /d "%~dp0"
call .venv\Scripts\activate 2>nul
python telegram_bot.py
pause
