# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mac-metadata-cleaner.py'],          # Main script file
    pathex=[],                 # Additional Python path locations
    binaries=[],              # Additional binary files (DLLs, etc.)
    datas=[],                 # Additional non-binary files (configs, resources, etc.)
    
    # Explicitly list dependencies that PyInstaller might miss
    hiddenimports=[
        'windnd',             # For drag and drop support
        'tkinter',            # GUI framework
        'tkinter.ttk',        # For themed widgets
        'tkinter.font',       # For custom fonts
    ],
    
    hookspath=[],             # Custom hooks for special handling
    hooksconfig={},           # Configuration for hooks
    runtime_hooks=[],         # Scripts to run before main program
    excludes=[               # Modules to explicitly exclude
        'matplotlib',         # Example: exclude unused large libraries
        'numpy',
        'PIL',
    ],
    
    # Don't change these unless you have specific needs
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Bundle all the files
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mac_metadata_cleaner',    # Name of the output executable
    debug=False,                    # Include debugging info?
    bootloader_ignore_signals=False,
    strip=False,                    # Strip symbols from binary?
    upx=True,                      # Use UPX compression?
    upx_exclude=[],                # Files to not compress
    runtime_tmpdir=None,           # Temporary directory for unpacking
    console=False,                 # Show console window?
    disable_windowed_traceback=False,
    target_arch=None,              # Target architecture (None = same as Python)
    codesign_identity=None,        # Code signing identity (macOS)
    entitlements_file=None,        # Entitlements file (macOS)
    
    # Optional: Add icon
    # icon='path/to/icon.ico',     # Uncomment to add custom icon
)

# If you want to add a version file (Windows)
# version_file = 'file_version_info.txt'
# if os.path.isfile(version_file):
#     exe.version = version_file
