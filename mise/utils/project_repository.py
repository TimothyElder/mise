from __future__ import annotations

import sqlite3
from pathlib import Path

class ProjectRepository:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    @property
    def connection(self):
        return self.conn

    # ---- documents -------------------------------------------------
    def register_document(self, label: str, text_path: Path) -> int:
        cur = self.conn.execute(
            "INSERT INTO documents (label, text_path, created_at) "
            "VALUES (?, ?, datetime('now'))",
            (label, str(text_path)),
        )
        self.conn.commit()
        return cur.lastrowid

    def lookup_document_id(self, text_path: Path) -> int | None:
        row = self.conn.execute(
            "SELECT id FROM documents WHERE text_path = ?",
            (str(text_path),),
        ).fetchone()
        return row["id"] if row else None

    # ---- coded_segments --------------------------------------------
    def get_coded_segments(self, document_id: int):
        return self.conn.execute(
            "SELECT * FROM coded_segments "
            "WHERE document_id = ? "
            "ORDER BY start_offset",
            (document_id,),
        ).fetchall()

    def add_coded_segment(
        self,
        document_id: int,
        code_id,
        start_offset: int,
        end_offset: int,
        memo: str | None = None,
    ) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO coded_segments (
                document_id, code_id, start_offset, end_offset, memo, created_at
            )
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (document_id, str(code_id), start_offset, end_offset, memo),
        )
        self.conn.commit()
        return cur.lastrowid

    # ---- lifecycle -------------------------------------------------
    def close(self) -> None:
        self.conn.close()