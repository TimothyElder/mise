import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    # In bundle, datas went to "mise/assets", so BASE_DIR should be "mise"
    BASE_DIR = Path(sys._MEIPASS) / "mise"
else:
    # From source, this is the "mise" package directory
    BASE_DIR = Path(__file__).resolve().parents[1]

ASSETS_DIR = BASE_DIR / "assets"

def asset_path(name: str) -> str:
    return str(ASSETS_DIR / name)