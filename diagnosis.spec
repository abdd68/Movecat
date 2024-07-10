# diagnosis.spec

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集 sklearn 包中的所有数据文件
sklearn_data_files = collect_data_files('sklearn')

a = Analysis(
    ['diagnosis_2.py'],
    pathex=[],
    binaries=[],
    datas=[('models/GBT.pkl', 'models'), ('image/*', 'image'), ('translations.json', '.')] + sklearn_data_files,
    hiddenimports=collect_submodules('sklearn'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='diagnosis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False
)
