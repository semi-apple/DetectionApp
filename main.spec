# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['/Users/kunzhou/Desktop/DetectionApp'],
    binaries=[],
    datas=[
        ('Application/*', 'Application'),
        ('Exceptions/*', 'Exceptions'),
        ('IO/*', 'IO'),
        ('Models/*', 'Models'),
        ('Widgets/*', 'Widgets'),
        ('dataset/*', 'dataset'),
        ('venv/lib/python3.11/site-packages/ultralytics/cfg/default.yaml', 'ultralytics/cfg'),
    ],
    hiddenimports=['ultralytics'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['detect.icns'],
)
app = BUNDLE(
    exe,
    name='main.app',
    icon='detect.icns',
    bundle_identifier=None,
)
