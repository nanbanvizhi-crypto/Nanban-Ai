@echo off
rem Dark OSINT - Tor terminal browser + 15 OSINT commands (runs inside Kali WSL).
rem   dark-osint.bat            start the browser
rem   dark-osint.bat install    install / update it inside Kali
rem   dark-osint.bat <args>     e.g.  dark-osint.bat check   |   dark-osint.bat search ransomware
title Dark OSINT
if /i "%~1"=="install" (
  wsl.exe -d kali-linux -u root -- bash "$(wslpath '%~dp0assets\kali_desktop\dark-osint-install.sh')" nanbanlinux
  goto :eof
)
wsl.exe -d kali-linux -- test -x /usr/local/bin/dark-osint
if errorlevel 1 (
  echo dark-osint is not installed in Kali yet - installing...
  wsl.exe -d kali-linux -u root -- bash "$(wslpath '%~dp0assets\kali_desktop\dark-osint-install.sh')" nanbanlinux
)
wsl.exe -d kali-linux --cd ~ -- /usr/local/bin/dark-osint %*
