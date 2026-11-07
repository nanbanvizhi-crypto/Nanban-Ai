@echo off
chcp 65001 >nul
title Local AI Agent - Setup
cd /d "%~dp0"
set PYTHONUTF8=1

echo.
echo ============================================
echo    Local AI Agent - one-time setup
echo ============================================
echo.

rem ---- Find a supported Python: 3.13 first, then 3.14, then 3.12.
rem ---- Python 3.15 is too new: some libraries have no Windows packages for it yet.
set "PY="
for %%v in (3.13 3.14 3.12) do (
    if not defined PY (
        py -%%v --version >nul 2>nul
        if not errorlevel 1 set "PY=py -%%v"
    )
)
if not defined PY (
    python -c "import sys; sys.exit(0 if (3,12) <= sys.version_info[:2] < (3,15) else 1)" >nul 2>nul
    if not errorlevel 1 set "PY=python"
)
if not defined PY (
    echo [X] Python 3.13 is needed. Python 3.15 is too new for some libraries.
    echo.
    echo     Open Command Prompt and run:   py install 3.13
    echo     Then run setup.bat again.
    echo.
    echo     No 'py' command? Install Python 3.13 from https://www.python.org/downloads/
    echo     and tick "Add python.exe to PATH" during install.
    pause
    exit /b 1
)
echo Using Python:
%PY% --version

where ollama >nul 2>nul
if errorlevel 1 (
    echo [X] Ollama is not installed.
    echo     Download it from https://ollama.com/download , install it, then run setup.bat again.
    pause
    exit /b 1
)

echo [1/4] Creating a private Python environment...
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -c "import sys; sys.exit(0 if (3,12) <= sys.version_info[:2] < (3,15) else 1)" >nul 2>nul
    if errorlevel 1 (
        echo     Removing an old environment made with an unsupported Python version...
        rmdir /s /q .venv
    )
)
if not exist .venv\Scripts\activate.bat %PY% -m venv .venv
if not exist .venv\Scripts\activate.bat (
    echo [X] Could not create the Python environment.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat

echo [2/4] Installing Python libraries - takes a few minutes the first time...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [X] Library install failed. Check your internet connection and run setup.bat again.
    pause
    exit /b 1
)

for /f "delims=" %%m in ('python -c "import config; print(config.MODEL)"') do set CHAT_MODEL=%%m
for /f "delims=" %%m in ('python -c "import config; print(config.EMBED_MODEL)"') do set EMBED_MODEL=%%m

echo [3/4] Downloading the chat model %CHAT_MODEL% - about 5 GB, one time only...
ollama pull %CHAT_MODEL%
if errorlevel 1 (
    echo [X] Model download failed. Make sure the Ollama app is running, then run setup.bat again.
    pause
    exit /b 1
)

echo [4/4] Downloading the document search model %EMBED_MODEL%...
ollama pull %EMBED_MODEL%

echo.
choice /c YN /n /m "Add the 'nanban' command, to open the AI terminal from any folder? [Y/N] "
if errorlevel 2 goto skip_path
powershell -NoProfile -Command "$d = '%~dp0'.TrimEnd('\'); $p = [Environment]::GetEnvironmentVariable('Path', 'User'); if (-not $p) { $p = '' }; if (($p -split ';') -notcontains $d) { [Environment]::SetEnvironmentVariable('Path', ($p.TrimEnd(';') + ';' + $d).TrimStart(';'), 'User'); Write-Host 'Done. Open a NEW terminal in any folder and type: nanban' } else { Write-Host 'The nanban command is already set up.' }"
:skip_path

echo Creating Desktop shortcut...
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $d = [Environment]::GetFolderPath('Desktop'); $s = $ws.CreateShortcut($d + '\Nanban.lnk'); $s.TargetPath = '%~dp0start_nanban.bat'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = '%~dp0assets\nanban.ico'; $s.Description = 'Nanban - one click starts everything'; $s.Save()"

wsl.exe -e true >nul 2>nul
if errorlevel 1 (
    echo.
    echo Optional - full Linux terminal: open PowerShell as Administrator, run   wsl --install
    echo then restart the laptop and create your Ubuntu username and password.
)

echo.
echo ============================================
echo    Setup complete!
echo.
echo    Just double-click "Nanban" on your Desktop.
echo    ONE click starts everything: the app, the
echo    server/API, (the lab if enabled), and opens
echo    your browser. Nothing else to click.
echo ============================================
echo.
choice /c YN /n /m "Start Nanban now? [Y/N] "
if errorlevel 2 goto done
start "" "%~dp0start_nanban.bat"
:done
