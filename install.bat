@echo off
REM Installation script for StreamCut Pro (Windows)

echo ================================================
echo   StreamCut Pro - Installation Script
echo ================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found %PYTHON_VERSION%
echo.

REM Check FFmpeg
echo Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo Warning: FFmpeg is not installed or not in PATH
    echo.
    echo Please install FFmpeg:
    echo   Download from: https://ffmpeg.org/download.html
    echo   Or use: winget install FFmpeg
    echo.
    pause
) else (
    for /f "tokens=*" %%i in ('ffmpeg -version ^| findstr /C:"ffmpeg version"') do set FFMPEG_VERSION=%%i
    echo Found FFmpeg
)
echo.

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully
echo.

echo ================================================
echo   Installation Complete!
echo ================================================
echo.
echo To run StreamCut Pro:
echo   python main.py
echo.
echo Or double-click: run.bat
echo.
echo For more information, see README.md
echo.
pause
