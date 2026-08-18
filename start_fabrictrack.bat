@echo off
title FabricTrack Launcher
setlocal
set "CLOUDFLARED=C:\Program Files (x86)\cloudflared\cloudflared.exe"
set "PROJECT_DIR=E:\New folder\FabricTrack"

cd /d "%PROJECT_DIR%"

echo Starting Django server on port 8000...
start "FabricTrack Django" cmd /k "cd /d "%PROJECT_DIR%" && call .venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000"

echo Waiting 10 seconds for Django to be ready...
timeout /t 10 /nobreak > nul

echo Starting Cloudflare Tunnel (fabrictrack.uk)...
start "FabricTrack Tunnel" cmd /k ""%CLOUDFLARED%" --config "%PROJECT_DIR%\.cloudflared\config.yml" tunnel run fabricstrack"

echo.
echo ==========================================
echo  FabricTrack is running!
echo  URL: https://fabrictrack.uk
echo ==========================================
echo.
pause