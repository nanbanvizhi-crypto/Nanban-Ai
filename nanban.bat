@echo off
rem Type `nanban` in any terminal to open the Nanban AI terminal in that folder.
rem (setup.bat can add this folder to your PATH so the command works everywhere.)
chcp 65001 >nul
set PYTHONUTF8=1
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Please run setup.bat in the Nanban folder first.
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0terminal.py" %*
