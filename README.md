# JSON to CSV Converter

A PySide GUI application that converts JSON files to CSV format with proper comma handling and nested structure support.

## Features

- 🖥️ **User-friendly GUI** - Clean PySide interface
- ✅ **Proper CSV formatting** - Handles commas in values with automatic quoting
- 🔄 **Nested JSON support** - Flattens nested structures into CSV columns
- 📋 **Paste or file input** - Select JSON files or paste content directly
- 🚀 **Standalone executable** - Build a self-contained app (no Python required)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd jsontocsv

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
python json_to_csv_converter.py
```

1. Select a JSON file or paste JSON content
2. Click "Convert to CSV"
3. Choose output location

## Building Standalone Executable

Build a standalone app that doesn't require Python:

```bash
# Install build dependencies
pip install -r requirements-build.txt

# Build (macOS/Linux)
./build.sh

# Build (Windows)
build.bat
```

Output: `dist/JSONtoCSVConverter.app` (macOS) or `dist/JSONtoCSVConverter.exe` (Windows)

**macOS Note**: If you get a "cannot be opened" error, right-click the app → "Open" → "Open" in the dialog. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help.

## Example

**Input JSON:**
```json
{
  "name": "John Doe",
  "address": {
    "street": "123 Main St, Apt 4",
    "city": "New York"
  }
}
```

**Output CSV:**
```csv
"address_city","address_street","name"
"New York","123 Main St, Apt 4","John Doe"
```

All fields are quoted to ensure compatibility with tools like Salesforce Data Loader.

## How It Works

- **Comma handling**: All fields are quoted using Python's `csv` module
- **Column order**: Preserves JSON key order
- **Nested structures**: Flattens with underscore-separated keys (e.g., `address_city`)
- **Multiple records**: Supports arrays of objects

## Requirements

- Python 3.8+
- PySide6

## License

Open source - available for use.
