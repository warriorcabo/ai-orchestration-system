@echo off
echo =======================================
echo   Starting AI Orchestration System
echo =======================================

REM Kill any existing Python processes running app.py
taskkill /F /FI "WINDOWTITLE eq AI Orchestration System" /T >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq AI Orchestration*" >nul 2>&1

REM Activate virtual environment
call venv\Scripts\activate

REM Start the system in a new window
start "AI Orchestration System" cmd /k "python app.py"

REM Display information in the original window
echo.
echo AI Orchestration System has been started in a new window.
echo Dashboard is available at: http://localhost:5000
echo.
echo If you close the system window, you can restart it using this batch file.
echo.
pause
