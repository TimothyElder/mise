# mise.spec
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, BUNDLE
import os

# PyInstaller does not set __file__ — use cwd instead (build script cds to project root)
project_root = Path(os.getcwd()).resolve()
src_dir = project_root / "src"

assets_src = src_dir / "mise" / "assets"

if sys.platform == "win32":
    icon_file = assets_src / "mise.ico"
else:
    icon_file = assets_src /  "mise.icns"

block_cipher = None

# Include all mise submodules
hidden_imports = collect_submodules("mise")

# datas must be a sequence of 2-tuples: (source, target-relative-dir)
datas = [
    (str(assets_src), "mise/assets"),
]

a = Analysis(
    ['src/mise/__main__.py'],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="Mise",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=str(icon_file),
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="Mise.app",
        icon=str(icon_file),
        bundle_identifier="org.mise.qda",
    )