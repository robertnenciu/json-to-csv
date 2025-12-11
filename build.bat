@echo off
REM Build script for JSON to CSV Converter (Windows)
REM Creates a standalone executable using PyInstaller

echo Building JSON to CSV Converter...
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install -r requirements-build.txt
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Build the executable
echo Building executable...
pyinstaller build.spec --clean

echo.
echo Build complete!
echo Executable location: dist\JSONtoCSVConverter.exe
echo.

pause

