@echo off
REM ============================================================================
REM  Nanban Portable — zero-install launcher.
REM
REM  First run (one-time, offline-friendly where possible):
REM    * Finds or downloads an embedded Python runtime into runtime\
REM    * Installs the Python dependencies into runtime\Lib\site-packages
REM    * Downloads BusyBox for Linux-style commands (no WSL needed)
REM    * Downloads the bundled AI model (~1 GB) into models\
REM
REM  Every run after that: straight to the app in your browser, no checks.
REM
REM  NOTHING is installed on Windows itself — everything lives in this folder.
REM  Copy the whole folder to a USB stick or another PC and it works the same.
REM ============================================================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "PY_VER=3.13.1"
set "PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-embed-amd64.zip"
set "GETPIP=https://bootstrap.pypa.io/get-pip.py"
set "BUSYBOX_URL=https://frippery.org/files/busybox/busybox.exe"
set "RUNTIME=runtime"
set "PYEXE=%RUNTIME%\python.exe"
set "FLAG=%RUNTIME%\.installed"

REM --- Step 1: embedded Python runtime -----------------------------------------
if not exist "%PYEXE%" (
    echo [Nanban] First run: downloading portable Python %PY_VER% ^(~15 MB^)...
    if not exist "%RUNTIME%" mkdir "%RUNTIME%"
    powershell -NoProfile -Command ^
        "try { Invoke-WebRequest -UseBasicParsing -Uri '%PY_URL%' -OutFile '%RUNTIME%\py.zip'; " ^
        "Expand-Archive -Path '%RUNTIME%\py.zip' -DestinationPath '%RUNTIME%' -Force; " ^
        "Remove-Item '%RUNTIME%\py.zip' } catch { exit 1 }"
    if errorlevel 1 (
        echo [Nanban] Could not download Python. Check your internet, then run this again.
        pause & exit /b 1
    )
    REM allow pip / site-packages inside the embedded distro
    for %%P in ("%RUNTIME%\python*._pth") do (
        powershell -NoProfile -Command ^
            "(Get-Content '%%~P') -replace '#import site','import site' | Set-Content '%%~P'"
    )
)

REM --- Step 2: pip + Nanban's dependencies -------------------------------------
if not exist "%FLAG%" (
    echo [Nanban] Installing Nanban's libraries into this folder ^(one time^)...
    if not exist "%RUNTIME%\get-pip.py" (
        powershell -NoProfile -Command "Invoke-WebRequest -UseBasicParsing -Uri '%GETPIP%' -OutFile '%RUNTIME%\get-pip.py'"
    )
    "%PYEXE%" "%RUNTIME%\get-pip.py" --no-warn-script-location
    "%PYEXE%" -m pip install --no-warn-script-location -r requirements.txt
    "%PYEXE%" -m pip install --no-warn-script-location llama-cpp-python
    if errorlevel 1 (
        echo [Nanban] Library install failed. Fix the error above and run again.
        pause & exit /b 1
    )
    echo installed> "%FLAG%"
)

REM --- Step 3: BusyBox (Linux-style terminal, no WSL needed) -------------------
if not exist "bin\busybox.exe" (
    echo [Nanban] Downloading BusyBox ^(Linux commands, ~1 MB, no WSL needed^)...
    if not exist "bin" mkdir "bin"
    powershell -NoProfile -Command ^
        "try { Invoke-WebRequest -UseBasicParsing -Uri '%BUSYBOX_URL%' -OutFile 'bin\busybox.exe' } catch { Write-Host 'BusyBox download skipped — Terminal tab will use PowerShell instead.' }"
)

REM --- Step 4: AI model (downloaded on first open by local_runtime.py) ---------
REM The runtime pulls it the first time the model is used, so startup stays fast.

REM --- Step 5: run! ------------------------------------------------------------
echo [Nanban] Starting Nanban...
"%PYEXE%" app.py
endlocal
