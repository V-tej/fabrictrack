@echo off
title FabricTrack Updater
echo =======================================
echo   FabricTrack -- Updating...
echo =======================================
echo.

cd /d "%~dp0"

echo [1/5] Stopping any running servers...
taskkill /f /im python.exe 2>nul
taskkill /f /im cloudflared.exe 2>nul
timeout /t 2 /nobreak > nul

echo [2/5] Pulling latest code from GitHub...
git pull origin main
if %errorlevel% neq 0 (
    echo.
    echo ERROR: git pull failed. Check your internet connection.
    echo Make sure git is installed: https://git-scm.com
    pause
    exit /b 1
)

echo [3/5] Installing any new Python dependencies...
pip install -r requirements.txt --quiet

echo [4/5] Applying database migrations...
python manage.py migrate

echo [5/5] Collecting static files...
python manage.py collectstatic --noinput

echo.
echo =======================================
echo   Update COMPLETE!
echo   Starting FabricTrack now...
echo =======================================
timeout /t 3 /nobreak > nul

call start_fabrictrack.bat
