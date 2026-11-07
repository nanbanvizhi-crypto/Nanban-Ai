@echo off
chcp 65001 >nul
title Nanban Security Lab - Stop
cd /d "%~dp0"
echo Stopping the practice lab...
docker compose down
echo Done. The targets are stopped.
pause
