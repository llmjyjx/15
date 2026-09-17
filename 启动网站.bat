@echo off
setlocal
cd /d "%~dp0"
title Xiangpan Art V26
set "PORT=5033"
echo ========================================
echo   Xiangpan Art Server - PORT %PORT%
echo ========================================
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    echo Stopping PID %%a ...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul
where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py"
) else (
    set "PY=python"
)
%PY% -m pip install -r requirements.txt
echo.
echo Local: http://127.0.0.1:%PORT%/
echo LAN:   http://YOUR-PC-IP:%PORT%/
echo Admin: http://127.0.0.1:%PORT%/admin.html
echo.
%PY% server.py
pause
