import sqlite3
from pathlib import Path

import logging
log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE documents (
    id                INTEGER PRIMARY KEY,
    original_filename TEXT,
    display_name      TEXT NOT NULL,
    text_path         TEXT NOT NULL,
    created_at        TEXT NOT NULL,
    doc_uuid          TEXT UNIQUE NOT NULL
);

CREATE TABLE codes (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    parent_id TEXT REFERENCES codes(id),
    description TEXT,
    color TEXT,
    sort_order INTEGER
);

CREATE TABLE coded_segments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id   INTEGER NOT NULL REFERENCES documents(id),
    code_id       TEXT NOT NULL REFERENCES codes(id),
    start_offset  INTEGER NOT NULL,
    end_offset    INTEGER NOT NULL,
    memo          TEXT,
    created_at    TEXT NOT NULL
);
"""

def initialize_database(project_root: Path):
    """
    Create project.db with all documnets, codes, and coded_segments tables.
    """
    db_path = Path(project_root) / "project.db"

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()