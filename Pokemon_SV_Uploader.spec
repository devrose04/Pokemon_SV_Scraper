# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pokemon_sv_uploader.py'],
    pathex=[],
    binaries=[],
    datas=[('credentials.json', '.'), ('sample_trainer_data.json', '.')],
    hiddenimports=['requests', 'bs4', 'google.oauth2.service_account', 'googleapiclient.discovery', 'googleapiclient.errors', 'tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Pokemon_SV_Uploader',
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
    icon=['pokemon_icon.ico'],
)
