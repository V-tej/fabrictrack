@echo off
title FabricTrack Updater
setlocal
set "PROJECT_DIR=C:\Users\Administrator\fabrictrack"

echo =======================================
echo   FabricTrack — Updating...
echo =======================================

cd /d "%PROJECT_DIR%"

echo Stopping running servers...
taskkill /f /im python.exe 2>nul
taskkill /f /im cloudflared.exe 2>nul

timeout /t 2

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Pulling latest code from GitHub...
git pull origin main

echo Installing any new dependencies...
pip install -r requirements.txt --quiet

echo Applying database changes (migrations)...
python manage.py migrate

echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Update complete! Starting FabricTrack...
timeout /t 2

call start_fabrictrack.bat