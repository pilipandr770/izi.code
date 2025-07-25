@echo off
echo ========================================
echo    SaaS Shop Flask Application Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

:: Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your API keys:
    echo - STRIPE_PUBLISHABLE_KEY
    echo - STRIPE_SECRET_KEY  
    echo - OPENAI_API_KEY
    echo - OPENAI_ASSISTANT_ID
    echo.
)

:: Initialize database
echo Initializing database...
set FLASK_APP=run.py
flask init-db

echo.
echo ========================================
echo         Setup Complete!
echo ========================================
echo.
echo To start the development server, run:
echo   python run.py
echo.
echo Admin panel will be available at:
echo   http://localhost:5000/admin
echo.
echo Default admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Don't forget to edit your .env file!
echo.
pause
