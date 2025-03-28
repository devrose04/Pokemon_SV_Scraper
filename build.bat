@echo off
setlocal enabledelayedexpansion

echo Pokemon SV Uploader - Building Executable...

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

REM Build the executable
echo Building executable...
python build_exe.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build executable.
    pause
    exit /b 1
)

REM Deactivate virtual environment
call deactivate

echo Build completed! You can find the executable in the 'dist' directory.
echo.
echo Remember to copy credentials.json to the same directory as the executable.
pause 