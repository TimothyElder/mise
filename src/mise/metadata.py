import json
from pathlib import Path

import logging
log = logging.getLogger(__name__)

DEFAULT_METADATA = {
    "version": 1,
    "ui": {
        "theme": "light",
        "font_size": 12
    },
    "project": {
        "immutable_docs": True
    }
}

def initialize_metadata(project_root: Path):
    meta_dir = Path(project_root) / "meta"
    config_path = meta_dir / "config.json"
    config_path.write_text(
        json.dumps(DEFAULT_METADATA, indent=2),
        encoding="utf-8"
    )