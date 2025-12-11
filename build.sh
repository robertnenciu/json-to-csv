#!/bin/bash
# Build script for JSON to CSV Converter
# Creates a standalone executable using PyInstaller

set -e  # Exit on error

echo "Building JSON to CSV Converter..."
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install -r requirements-build.txt
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist __pycache__

# Build the executable
echo "Building executable..."
pyinstaller build.spec --clean

echo ""
echo "Build complete!"
echo ""

# Check what was created
if [ -d "dist/JSONtoCSVConverter.app" ]; then
    echo "✓ macOS App Bundle created: dist/JSONtoCSVConverter.app"
    echo ""
    echo "To run the app:"
    echo "  open dist/JSONtoCSVConverter.app"
    echo ""
    echo "Or double-click JSONtoCSVConverter.app in Finder"
elif [ -f "dist/JSONtoCSVConverter" ]; then
    echo "✓ Executable created: dist/JSONtoCSVConverter"
    echo ""
    echo "To run:"
    echo "  ./dist/JSONtoCSVConverter"
fi

echo ""
echo "IMPORTANT - macOS Security:"
echo "If you get a 'cannot be opened' error:"
echo "1. Right-click (or Control-click) the app"
echo "2. Select 'Open' from the context menu"
echo "3. Click 'Open' in the security dialog"
echo ""
echo "Alternatively:"
echo "1. Go to System Preferences > Security & Privacy"
echo "2. Click 'Open Anyway' next to the blocked app message"

