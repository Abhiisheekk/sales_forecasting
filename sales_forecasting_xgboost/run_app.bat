@echo off
REM Quick start script for Streamlit Sales Forecasting App
REM Run this file to start the application

cd /d "%~dp0"

echo ========================================
echo Automobile Sales Forecasting System
echo ========================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Checking dependencies...
pip list | find "streamlit" > nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Streamlit application...
echo.
echo The app will open in your default browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run streamlit_app.py

pause
