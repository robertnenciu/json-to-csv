# -*- mode: python ; coding: utf-8 -*-

import sys

block_cipher = None

a = Analysis(
    ['json_to_csv_converter.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JSONtoCSVConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Set to False to avoid compression issues on some systems
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file path here if you have one (e.g., 'icon.icns' for macOS)
)

# For macOS, wrap the executable in an .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='JSONtoCSVConverter.app',
        icon=None,
        bundle_identifier='com.jsontocsv.converter',
    )

