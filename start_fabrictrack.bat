@echo off
title FabricTrack Launcher
setlocal
set "CLOUDFLARED=C:\Program Files (x86)\cloudflared\cloudflared.exe"
set "PROJECT_DIR=%~dp0"

cd /d "%PROJECT_DIR%"

echo Starting Django server on port 8000...
start "FabricTrack Django" cmd /k "cd /d "%PROJECT_DIR%" && call .venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

echo Waiting 10 seconds for Django to be ready...
timeout /t 10 /nobreak > nul

echo Starting Cloudflare Tunnel (fabrictrack.uk)...
start "FabricTrack Tunnel" cmd /k ""%CLOUDFLARED%" --config "%PROJECT_DIR%.cloudflared\config.yml" tunnel run --credentials-file "%PROJECT_DIR%.cloudflared\6fe9a24b-06d8-4611-9a94-40db9e6f3f0f.json""

echo.
echo ==========================================
echo  FabricTrack is running!
echo  URL: https://fabrictrack.uk
echo ==========================================
echo.
pause