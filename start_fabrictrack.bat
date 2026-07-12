@echo off
title FabricTrack Launcher
echo =======================================
echo   FabricTrack -- Starting...
echo =======================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Django server on port 8000...
start "FabricTrack Django" cmd /k "cd /d "%~dp0" && python manage.py runserver 0.0.0.0:8000"

echo Waiting for Django to start...
timeout /t 6 /nobreak > nul

echo [2/2] Starting Cloudflare Tunnel...
start "FabricTrack Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"

echo.
echo =======================================
echo   FabricTrack is RUNNING!
echo   Check the "FabricTrack Tunnel" window
echo   for the public URL.
echo   Share that URL with your users.
echo =======================================
echo.
pause
