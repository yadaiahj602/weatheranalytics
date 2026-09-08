@echo off
REM ==============================================================================
REM WeatherPlatform — Production / Local Deployment Runner
REM ==============================================================================

echo.
echo ========================================================
echo   WeatherPlatform Live Analytics - Deployment Runner
echo ========================================================
echo.

SET PYTHONUNBUFFERED=1
SET DJANGO_SETTINGS_MODULE=config.settings.local

echo [1/4] Checking Python environment...
python --version
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.10+
    pause
    exit /b 1
)

echo.
echo [2/4] Applying database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [WARNING] Migration warning encountered, proceeding with existing schema.
)

echo.
echo [3/4] Collecting static assets...
python manage.py collectstatic --noinput

echo.
echo [4/4] Starting WeatherPlatform Production Web Server on http://0.0.0.0:8000 ...
echo [INFO] First page: http://127.0.0.1:8000/ (Login & Credential Storage Form)
echo [INFO] Dashboard:  http://127.0.0.1:8000/dashboard/
echo [INFO] Historical: http://127.0.0.1:8000/historical/
echo.
python manage.py runserver 0.0.0.0:8000
