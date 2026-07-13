@echo off
title FabricTrack Launcher
setlocal
set "CLOUDFLARED=C:\Program Files (x86)\cloudflared\cloudflared.exe"
set "PROJECT_DIR=C:\Users\Administrator\fabrictrack"

cd /d "%PROJECT_DIR%"

echo Starting Django server on port 8000...
start "FabricTrack Django" cmd /k "cd /d "%PROJECT_DIR%" && call .venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000 > django_log.txt 2>&1"

echo Waiting 15 seconds for Django and PostgreSQL to be ready...
timeout /t 15 /nobreak > nul

echo Starting Cloudflare Tunnel...
start "FabricTrack Tunnel" cmd /k ""%CLOUDFLARED%" tunnel --url http://localhost:8000"

pause