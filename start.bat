@echo off
echo ========================================
echo   ZConnect - Teams-like App
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet

echo [2/3] Running migrations...
python manage.py migrate --run-syncdb

echo [3/3] Starting server...
echo.
echo  App running at: http://127.0.0.1:8000
echo  Press Ctrl+C to stop
echo.
python manage.py runserver 0.0.0.0:8002
