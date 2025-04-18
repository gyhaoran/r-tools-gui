# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs, get_package_paths
from PyInstaller import isolated
import os


z3_binaries = collect_dynamic_libs('z3')

a = Analysis(
    ['pysmt_demo.py'],
    pathex=[],
    binaries=[
        *z3_binaries,
    ],
    datas=[
        *collect_data_files('pysmt', include_py_files=True),
        *collect_data_files('Cython',  include_py_files=True),
        *collect_data_files('distutils', include_py_files=True)
    ],
    hiddenimports=[
        'distutils',
        'distutils.unixccompiler',
        'Cython.Build',
        'pyximport',
    ],
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
    name='pysmt_demo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
