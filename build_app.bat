@echo off
chcp 65001 >nul
title Build Nanban.exe
cd /d "%~dp0"
set PYTHONUTF8=1

if not exist .venv\Scripts\python.exe (
    echo Please run setup.bat first.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat

echo Installing the packager (one time)...
pip install --quiet pyinstaller
if errorlevel 1 (
    echo [X] Could not install PyInstaller. Check your internet connection.
    pause
    exit /b 1
)

echo Building Nanban.exe ... (1-3 minutes)
pyinstaller --noconfirm --clean --onefile --noconsole --name Nanban ^
    --icon assets\nanban.ico ^
    --hidden-import pystray._win32 ^
    --exclude-module gradio --exclude-module numpy --exclude-module torch ^
    launcher.py
if errorlevel 1 (
    echo [X] Build failed. You can still use start.bat / start_terminal.bat.
    pause
    exit /b 1
)

copy /y dist\Nanban.exe Nanban.exe >nul
rmdir /s /q build dist 2>nul
del /q Nanban.spec 2>nul

powershell -NoProfile -Command ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Nanban.lnk');" ^
  "$s.TargetPath = '%~dp0Nanban.exe'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = '%~dp0assets\nanban.ico'; $s.Description = 'Nanban - local AI'; $s.Save()"

echo.
echo ============================================
echo    Done! Nanban.exe is in this folder and a
echo    "Nanban" shortcut is on your Desktop.
echo    Double-click it: the icon appears in the
echo    system tray (bottom-right, near the clock).
echo ============================================
pause
