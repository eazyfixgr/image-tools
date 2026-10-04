@echo off
echo ========================================
echo Image Resizer - Quick Start
echo ========================================
echo.
echo Checking Python installation...
python --version
echo.

REM Install packages directly
echo Installing packages (this may take a moment)...
python -m pip install --user Pillow tkinterdnd2

echo.
echo ========================================
echo Starting Image Resizer...
echo ========================================
echo.

REM Run with the same Python
python "%~dp0image_resizer.py"

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to run Image Resizer
    echo ========================================
    echo.
    echo If you see a missing module error, try:
    echo 1. Close this window
    echo 2. Open Command Prompt as Administrator
    echo 3. Run: pip install Pillow tkinterdnd2
    echo 4. Then run this file again
    echo.
)

pause
