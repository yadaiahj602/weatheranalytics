# ==============================================================================
# WeatherPlatform — PowerShell Deployment Runner
# ==============================================================================

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  WeatherPlatform Live Analytics - Deployment Runner" -ForegroundColor White
Write-Host "========================================================`n" -ForegroundColor Cyan

$env:PYTHONUNBUFFERED = "1"
$env:DJANGO_SETTINGS_MODULE = "config.settings.local"

Write-Host "[1/4] Checking Python environment..." -ForegroundColor Yellow
python --version

Write-Host "`n[2/4] Applying database migrations..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "`n[3/4] Collecting static assets..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

Write-Host "`n[4/4] Starting WeatherPlatform Web Server on http://0.0.0.0:8000 ..." -ForegroundColor Green
Write-Host "[INFO] First page: http://127.0.0.1:8000/ (Login & Credential Storage Form)" -ForegroundColor Cyan
Write-Host "[INFO] Dashboard:  http://127.0.0.1:8000/dashboard/" -ForegroundColor Cyan
Write-Host "[INFO] Historical: http://127.0.0.1:8000/historical/" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver 0.0.0.0:8000
