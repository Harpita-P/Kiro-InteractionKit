@echo off
REM Kiro MotionMagic Setup Script for Windows

echo ==================================
echo Kiro MotionMagic Setup
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
echo.

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Test camera
echo Testing camera access...
python -c "import cv2; cap = cv2.VideoCapture(0); success = cap.isOpened(); cap.release(); exit(0 if success else 1)"

if %ERRORLEVEL% EQU 0 (
    echo Camera accessible
    echo.
    echo ==================================
    echo Environment configured and camera accessible.
    echo ==================================
) else (
    echo Camera not accessible
    echo.
    echo ==================================
    echo Environment configured but camera not accessible.
    echo Please check camera permissions and connections.
    echo ==================================
)
pause
