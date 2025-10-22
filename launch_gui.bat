@echo off
REM Silhouette Card Maker - Improved Launcher
REM =========================================
REM This launcher provides better error handling and setup

echo Starting Silhouette Card Maker...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Run the PowerShell GUI
echo Launching application...
powershell -ExecutionPolicy Bypass -File "gui.ps1"

REM Check if launch was successful
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo.
    echo Troubleshooting:
    echo 1. Make sure Python is installed and in PATH
    echo 2. Make sure PowerShell execution policy allows scripts
    echo 3. Try running: powershell -ExecutionPolicy Bypass -File "gui.ps1"
    echo.
    pause
    exit /b 1
)

echo Application closed.
pause
