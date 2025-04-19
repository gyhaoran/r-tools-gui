# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, get_package_paths
from PyInstaller import isolated
import os

block_cipher = None

project_root = '/home/ranhaooge/code/python/r-tools-gui'

a = Analysis(
    ['main.py'],
    pathex=[
        project_root,
        os.path.join(project_root, 'app'),
        os.path.join(project_root, 'backend'),
        os.path.join(project_root, 'core')
    ],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'ui/icons'), 'ui/icons'),
        (os.path.join(project_root, 'plugins'), 'plugins'),
    ],
    hiddenimports=[
        *collect_submodules('app', filter=lambda name: True),
        *collect_submodules('.backend.lef_parser', filter=lambda name: True),
        *collect_submodules('core', filter=lambda name: True),
        *collect_submodules('plugins', filter=lambda name: True),
    ],
    hookspath=[],         
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'torch.*'],
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
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
