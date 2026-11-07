@echo off
chcp 65001 >nul
title Nanban Update
cd /d "%~dp0"
echo.
echo ============================================
echo    Updating Nanban to the latest version
echo ============================================
echo.
if exist .git (
    git pull --ff-only
) else (
    echo This copy isn't a Git clone, so there's nothing to pull from.
    echo To enable updates: put Nanban on GitHub ^(see DEPLOY.md^), clone it, and run from the clone.
    pause
    exit /b 0
)
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Updating dependencies...
    pip install -q -r requirements.txt
)
echo.
echo Done. Start Nanban again to use the new version.
pause
