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
    
    # ---- codes ------------------------------------------------------
    def list_codes(self):
        """
        Return all codes as sqlite Row objects.
        Expected columns: id, label, parent_id, description, color, sort_order
        """
        return self.conn.execute(
            """
            SELECT id, label, parent_id, description, color, sort_order
            FROM codes
            ORDER BY sort_order, label
            """
        ).fetchall()

    def next_code_sort_order(self) -> int:
        row = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), 0) AS max_so FROM codes"
        ).fetchone()
        return (row["max_so"] or 0) + 1

    def add_code(self, label, parent_id=None, description="", color=None):
        import uuid

        code_id = str(uuid.uuid4())
        sort_order = self.next_code_sort_order()

        self.conn.execute(
            """
            INSERT INTO codes (id, label, parent_id, description, color, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (code_id, label, parent_id, description, color, sort_order),
        )
        self.conn.commit()
        return code_id
    
    def update_code(self, code_id, label=None, parent_id=None, description=None, color=None):
        fields = []
        values = []

        if label is not None:
            fields.append("label = ?")
            values.append(label)

        if parent_id is not None:
            fields.append("parent_id = ?")
            values.append(parent_id)

        if description is not None:
            fields.append("description = ?")
            values.append(description)

        if color is not None:
            fields.append("color = ?")
            values.append(color)

        if not fields:
            return 0  # nothing to update

        sql = f"UPDATE codes SET {', '.join(fields)} WHERE id = ?;"
        values.append(code_id)

        cur = self.conn.execute(sql, values)
        self.conn.commit()
        return cur.rowcount

    # ---- coded_segments --------------------------------------------
    def get_coded_segments(self, document_id: int):
        return self.conn.execute(
            """
            SELECT
                cs.*,
                c.color AS code_color
            FROM coded_segments AS cs
            LEFT JOIN codes AS c
                ON cs.code_id = c.id
            WHERE cs.document_id = ?
            ORDER BY cs.start_offset
            """,
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