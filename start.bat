@echo off
title SaaS Shop - Development Server

:: Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Set environment variables
set FLASK_APP=run.py
set FLASK_ENV=development
set FLASK_DEBUG=1

:: Start the development server
echo Starting SaaS Shop development server...
echo.
echo Server will be available at: http://localhost:5000
echo Admin panel: http://localhost:5000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py
