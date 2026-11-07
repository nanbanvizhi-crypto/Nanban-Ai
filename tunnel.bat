@echo off
chcp 65001 >nul
title Nanban Public Tunnel
cd /d "%~dp0"

echo.
echo ============================================
echo    Nanban Public URL (Cloudflare Tunnel)
echo ============================================
echo.
echo This gives your running Nanban a public https URL so you can reach it
echo from your phone or anywhere. Your laptop must stay on, and Nanban must
echo already be running (double-click Nanban first).
echo.

where cloudflared >nul 2>nul
if errorlevel 1 (
    echo [X] cloudflared is not installed.
    echo     Download it from:
    echo     https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
    echo     Install it, then run tunnel.bat again.
    pause
    exit /b 1
)

rem Read the port Nanban serves on from config.py (SERVER_PORT if server mode, else WEB_PORT)
for /f "delims=" %%p in ('.venv\Scripts\python.exe -c "import config; print(config.SERVER_PORT if (config.USERS or config.API_KEYS) else config.WEB_PORT)"') do set NB_PORT=%%p

echo Creating a public URL for http://localhost:%NB_PORT% ...
echo (Look for the https://xxxxx.trycloudflare.com link below — that's your public URL.)
echo Press Ctrl+C here to close the tunnel.
echo.
cloudflared tunnel --url http://localhost:%NB_PORT%
pause
