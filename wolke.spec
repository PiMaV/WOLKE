# PyInstaller spec for WOLKE. Build: pyinstaller wolke.spec
# Output: dist/WOLKE.exe (Windows) or dist/WOLKE (Unix)
import sys

from PyInstaller.utils.hooks import collect_all

block_cipher = None
hidden_imports = [
    'dash', 'dash.dash', 'dash.dependencies',
    'dash_bootstrap_components', 'dash_mantine_components',
    'flask', 'flask_socketio', 'engineio', 'socketio', 'eventlet',
    'engineio.async_drivers.eventlet',
    'engineio.async_drivers.threading',
    'eventlet.hubs.epolls', 'eventlet.hubs.kqueue', 'eventlet.hubs.selects',
    'dns', 'dns.resolver', 'dns.namedict', 'dns.e164',
    'plotly', 'pandas', 'numpy', 'werkzeug',
]

datas = []
binaries = []
# Dash component packages load package-info.json and JS assets at import time.
# eventlet/engineio need their async driver modules in the frozen bundle.
for pkg in (
    "dash_mantine_components",
    "dash_bootstrap_components",
    "dash",
    "plotly",
    "eventlet",
    "engineio",
    "socketio",
    "flask_socketio",
):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hidden_imports += pkg_hidden

a = Analysis(
    ['run_wolke.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
    console=sys.platform != "win32",
    disable_windowed_mode=False,
)
