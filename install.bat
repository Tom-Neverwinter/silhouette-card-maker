@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Silhouette Card Maker Installer
echo ========================================
echo.
echo Please choose which version to install:
echo 1. Tom-Neverwinter's version (https://github.com/Tom-Neverwinter/silhouette-card-maker)
echo 2. Alan-Cha's original version (https://github.com/Alan-Cha/silhouette-card-maker)
echo.
set /p VERSION_CHOICE="Enter your choice (1 or 2): "

if "%VERSION_CHOICE%"=="1" (
    set REPO_URL=https://github.com/Tom-Neverwinter/silhouette-card-maker.git
    set REPO_NAME=Tom-Neverwinter's version
    set FOLDER_NAME=silhouette-card-maker-tom
) else if "%VERSION_CHOICE%"=="2" (
    set REPO_URL=https://github.com/Alan-Cha/silhouette-card-maker.git
    set REPO_NAME=Alan-Cha's original version
    set FOLDER_NAME=silhouette-card-maker-alan
) else (
    echo Invalid choice. Please run the installer again and enter 1 or 2.
    pause
    exit /b 1
)

echo.
echo You selected: %REPO_NAME%
echo Repository: %REPO_URL%
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Cloning/Updating repository...
if exist "%FOLDER_NAME%" (
    echo Repository folder already exists. Updating...
    cd %FOLDER_NAME%
    git pull origin main
    if errorlevel 1 (
        echo WARNING: Failed to update repository. Continuing with existing version...
    ) else (
        echo Repository updated successfully.
    )
    cd ..
) else (
    git clone %REPO_URL% %FOLDER_NAME%
    if errorlevel 1 (
        echo ERROR: Failed to clone repository
        pause
        exit /b 1
    )
    echo Repository cloned successfully.
)
echo.

echo [2/5] Changing to repository directory...
cd %FOLDER_NAME%
if errorlevel 1 (
    echo ERROR: Failed to change directory
    pause
    exit /b 1
)
echo.

echo [3/5] Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully.
echo.

echo [4/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated.
echo.

echo [5/5] Installing/Updating Python packages from requirements.txt...
if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    echo Please make sure you're running this installer in the correct directory
    pause
    exit /b 1
)

pip install -r requirements.txt --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo Packages installed/updated successfully.
echo.

echo ========================================
echo Installation/Update Complete!
echo ========================================
echo.
echo Installed version: %REPO_NAME%
echo The repository is located at: %CD%
echo.
echo Next steps:
echo 1. Put your front images in the game\front\ folder
echo 2. Put your back image in the game\back\ folder
echo 3. Run the application (check the repository README for usage instructions)
echo.
echo To activate the virtual environment in the future:
echo   cd %FOLDER_NAME%
echo   venv\Scripts\activate.bat
echo.
echo To update in the future, just run this installer again!
echo.
pause