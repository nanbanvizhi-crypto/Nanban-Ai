@echo off
REM ============================================================================
REM  Build Nanban into a single Windows app (Nanban.exe).
REM
REM  Run this ONCE on your Windows laptop:   build_exe.bat
REM
REM  It uses PyInstaller to bundle Python + all libraries + Nanban's code into
REM  dist\Nanban\Nanban.exe. You can then copy that whole dist\Nanban folder
REM  anywhere (USB stick, another PC) and double-click Nanban.exe to run —
REM  no Python install needed on that machine.
REM
REM  Build takes ~5 minutes. Output size: ~400 MB (or ~1.5 GB if you drop a
REM  .gguf model into models\ before building, which makes it fully offline).
REM ============================================================================

setlocal
cd /d "%~dp0"

REM ---- 1. Make sure Python 3.13 is here (uses runtime\ from Portable mode, or system Python)
set "PYEXE="
if exist "runtime\python.exe" (
    set "PYEXE=runtime\python.exe"
) else (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYEXE set "PYEXE=%%P"
    )
)
if not defined PYEXE (
    echo [build] Python not found. Install Python 3.13 from python.org, or run Nanban-Portable.bat first to download the embedded runtime.
    pause & exit /b 1
)
echo [build] Using Python: %PYEXE%

REM ---- 2. Install Nanban's own libraries + PyInstaller
echo [build] Making sure dependencies are present (quick if already installed)...
"%PYEXE%" -m pip install --upgrade pip
"%PYEXE%" -m pip install -r requirements.txt
"%PYEXE%" -m pip install pyinstaller

REM ---- 3. Build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo [build] Bundling into dist\Nanban\Nanban.exe ...
"%PYEXE%" -m PyInstaller --noconfirm build_exe.spec
if errorlevel 1 (
    echo.
    echo [build] Build failed. Check the error above.
    pause & exit /b 1
)

echo.
echo [build] ============================================================
echo [build]  Done! Your app is at:  dist\Nanban\Nanban.exe
echo [build]  Double-click it to run. Copy the whole dist\Nanban folder
echo [build]  anywhere (USB stick, friend's PC) - it runs with no install.
echo [build] ============================================================
echo.
pause
endlocal
