@echo off
echo =======================================
echo   Starting AI Dashboard
echo =======================================

REM Kill any existing dashboard
taskkill /F /FI "WINDOWTITLE eq AI Dashboard" /T >nul 2>&1

REM Activate virtual environment
call venv\Scripts\activate

REM Start the dashboard in a new window
start "AI Dashboard" cmd /k "python start_dashboard.py"

echo.
echo Dashboard has been started in a new window.
echo Dashboard is available at: http://localhost:5000
echo.
pause
