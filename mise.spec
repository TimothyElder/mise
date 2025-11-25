# mise.spec
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, BUNDLE
from PyInstaller.building.datastruct import TOC

project_root = Path(__file__).resolve().parent
src_dir = project_root / "src"

block_cipher = None

# Include all submodules of mise to be safe
hidden_imports = collect_submodules("mise")

# Assets directory
assets_src = src_dir / "mise" / "assets"

datas = TOC()
datas.append((str(assets_src), "mise/assets", "DATA"))

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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,  # GUI app
    disable_windowed_traceback=False,
    argv_emulation=True,  # nice on macOS
    target_arch=None,
)

app = BUNDLE(
    exe,
    name="Mise.app",
    icon=None,  # add an .icns later
    bundle_identifier="org.mise.qda",
)