@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ==========================================
echo Silhouette Card Maker - Installer Launcher
echo ==========================================
echo.

REM 1. Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not found in PATH.
    echo Please install Python 3.8+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM 2. Check/Create Virtual Environment
if not exist "venv" (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo [INFO] Virtual environment found.
)

REM 3. Install/Update Dependencies
echo [INFO] Checking dependencies...
if not exist "requirements.txt" (
    echo [WARNING] requirements.txt not found! Skipping dependency install.
) else (
    REM Upgrade pip first to avoid annoying warnings
    ".\venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
    
    REM Install requirements
    ".\venv\Scripts\pip.exe" install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies are up to date.
)

echo.
echo [INFO] Launching Application...
echo.

REM 4. Launch PowerShell GUI
REM We execute with Bypass policy to ensure the script runs
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/gui.ps1"

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed or failed to start.
    pause
)

endlocal
