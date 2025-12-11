# Troubleshooting Guide

## macOS: "Couldn't open JSONtoCSVConverter.pkg"

### Problem
You're trying to open a `.pkg` file and getting an error.

### Solution
The `.pkg` file in the `build/` directory is an **intermediate build file** created by PyInstaller during the build process. You should **not** try to open it.

Instead, look for the actual application in the `dist/` directory:

1. **Open Finder** and navigate to the project folder
2. Look in the `dist/` folder for `JSONtoCSVConverter.app`
3. **Double-click** `JSONtoCSVConverter.app` to run it

### If the .app doesn't open (macOS Security)

If you get a "cannot be opened" or "damaged" error:

**Method 1: Right-click to open**
1. Right-click (or Control-click) on `JSONtoCSVConverter.app`
2. Select "Open" from the context menu
3. Click "Open" in the security dialog that appears

**Method 2: System Preferences**
1. Go to **System Preferences** > **Security & Privacy**
2. Look for a message about the blocked app
3. Click **"Open Anyway"**

**Method 3: Remove quarantine attribute (Terminal)**
```bash
xattr -d com.apple.quarantine dist/JSONtoCSVConverter.app
```

### Rebuilding the App

If you need to rebuild:

```bash
# Make sure you're in the project directory
cd /path/to/jsontocsv

# Activate your virtual environment (if using one)
source venv/bin/activate

# Install build dependencies (if not already installed)
pip install -r requirements-build.txt

# Run the build script
./build.sh
```

After building, check the `dist/` directory for `JSONtoCSVConverter.app`.

## Other Common Issues

### "PyInstaller not found"
Install it:
```bash
pip install -r requirements-build.txt
```

### Build fails with import errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

### App runs but crashes immediately
Check the console output or run from terminal:
```bash
./dist/JSONtoCSVConverter.app/Contents/MacOS/JSONtoCSVConverter
```

This will show error messages that can help diagnose the issue.

