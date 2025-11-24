from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]       # `mise/`
ASSETS_DIR = BASE_DIR / "assets"

def asset_path(name: str) -> str:
    return str(ASSETS_DIR / name)