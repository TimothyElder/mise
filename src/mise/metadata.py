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

MISE_INFO = """This is a mise project"""

def initialize_metadata(project_root: Path):
    meta_dir = Path(project_root) / "meta"
    config_path = meta_dir / "config.json"
    project_info = Path(project_root) / ".mise"

    config_path.write_text(
        json.dumps(DEFAULT_METADATA, indent=2),
        encoding="utf-8"
    )

    project_info.write_text(MISE_INFO, encoding="utf-8")