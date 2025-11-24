"""
project_repository.py

Manages all database calls.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import uuid

import logging
log = logging.getLogger(__name__)

class ProjectRepository:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    @property
    def connection(self):
        return self.conn

    # ---- documents -------------------------------------------------
    def register_document(self, original_filename: str, text_path: Path) -> int:
        cur = self.conn.execute(
            "INSERT INTO documents (original_filename, display_name, text_path, created_at, doc_uuid) "
            "VALUES (?, ?, ?, datetime('now'), ?)",
            (original_filename, original_filename, str(text_path), str(uuid.uuid4())),
        )
        self.conn.commit()
        return cur.lastrowid

    def lookup_document_id(self, text_path: Path) -> int | None:
        row = self.conn.execute(
            "SELECT id FROM documents WHERE text_path = ?",
            (str(text_path),),
        ).fetchone()
        return row["id"] if row else None
    
    def get_document_by_text_path(self, text_path: Path) -> Optional[Document]:
        cur = self.conn.execute(
            "SELECT id, display_name FROM documents WHERE text_path = ?",
            (str(text_path),),
        )
        row = cur.fetchone()
        return row
    
    def delete_document(self, document_id: int) -> tuple[int, str | None]:
        print(f"[DB] delete_document called with document_id={document_id!r}")

        # Get text_path before deletion
        cur = self.conn.execute(
            "SELECT text_path FROM documents WHERE id = ?",
            (document_id,),
        )
        row = cur.fetchone()
        if row is None:
            print("[DB] No document found for that id")
            return 0, None

        text_path = row[0]

        cur_segments = self.conn.execute(
            "DELETE FROM coded_segments WHERE document_id = ?",
            (document_id,),
        )
        cur_docs = self.conn.execute(
            "DELETE FROM documents WHERE id = ?",
            (document_id,),
        )
        self.conn.commit()

        print(
            f"[DB] deleted {cur_segments.rowcount} coded_segments, "
            f"{cur_docs.rowcount} documents"
        )
        return cur_docs.rowcount, text_path

    def rename_document_db(self, new_display_name, document_id):

        print(new_display_name)
        print(document_id)
        
        cur = self.conn.execute(
            """
            UPDATE documents
            SET display_name = ?
            WHERE id = ?;
            """,
            (new_display_name, document_id),
        )
        self.conn.commit()

        print(cur.rowcount)
        return cur.rowcount
    
    # ---- codes ------------------------------------------------------
    def lookup_code(self, code_id):
        """
        lookup current code by its id and return the assigned values
        """
        row = self.conn.execute(
            """
            SELECT label, parent_id, description, color, sort_order
            FROM codes
            WHERE id = ?;
            """,
            (code_id,),
        ).fetchone()

        if row is None:
            print(f"NO CODE matching ID == {code_id}")
        return(row)
    
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
    
    def update_code(self, code_id, label, parent_id, description, color):
        cur = self.conn.execute(
            """
            UPDATE codes
            SET label = ?,
                parent_id = ?,
                description = ?,
                color = ?
            WHERE id = ?;
            """,
            (label, parent_id, description, color, code_id),
        )
        self.conn.commit()
        return cur.rowcount
    
    def delete_code(self, code_id):
        
        # delete coded segments from the coded_segments table
        self.conn.execute("DELETE FROM coded_segments WHERE code_id = ?", (code_id,))

        # Delete the code from the codes table
        self.conn.execute("DELETE FROM codes WHERE id = ?", (code_id,))
        self.conn.commit()


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
    
    def get_segment_at_position(self, document_id, pos):
        row = self.conn.execute(
            """
            SELECT id, code_id, start_offset, end_offset
            FROM coded_segments
            WHERE document_id = ?
            AND start_offset <= ?
            AND end_offset >= ?
            LIMIT 1;
            """,
            (document_id, pos, pos),
        ).fetchone()
        return row
    
    def delete_segment(self, segment_id):
        # Delete the segment from the coded_segment by segment_id
        self.conn.execute("DELETE FROM coded_segments WHERE id = ?", (segment_id,))
        self.conn.commit()

    # ---- lifecycle -------------------------------------------------
    def close(self) -> None:
        self.conn.close()