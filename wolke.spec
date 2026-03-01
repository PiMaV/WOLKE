# PyInstaller spec for WOLKE. Build: pyinstaller wolke.spec
# Output: dist/WOLKE.exe (Windows) or dist/WOLKE (Unix)
import sys

block_cipher = None
hidden_imports = [
    'dash', 'dash.dash', 'dash.dependencies', 'dash_html_components', 'dash_core_components',
    'dash_bootstrap_components', 'dash_mantine_components',
    'flask', 'flask_socketio', 'engineio', 'socketio', 'eventlet',
    'plotly', 'pandas', 'numpy', 'werkzeug',
]

a = Analysis(
    ['run_wolke.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WOLKE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_mode=False,
)
