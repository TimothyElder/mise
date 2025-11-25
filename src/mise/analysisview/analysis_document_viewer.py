import logging
log = logging.getLogger(__name__)
from pathlib import Path

from PySide6.QtWidgets import (
    QVBoxLayout, QWidget,
    QTextBrowser, QDialog
)

from PySide6.QtGui import (
    QTextCursor, QTextCharFormat, 
    QColor)

from PySide6.QtCore import Qt

from ..utils.project_repository import ProjectRepository

class AnalysisDocumentViewerWidget(QWidget):

    def __init__(self, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        
        # Config
        self.repo = repo

        # State
        self.current_document_id = None

        # UI
        layout = QVBoxLayout(self)

        self.document_viewer = QTextBrowser()
        self.document_viewer.setText("Select a document to view its content.")
        layout.addWidget(self.document_viewer)

        # context menu for document viewer
        self.document_viewer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.document_viewer.customContextMenuRequested.connect(
            self.open_text_context_menu
        )

    def display_file_content(self, path: Path):
        """
        Display the content of the selected file in the document viewer.
        """
        try:
            # Use Path’s own API, not bare open(path, "r")
            content = path.read_text(encoding="utf-8")
            self.document_viewer.setPlainText(content)
        except Exception as e:
            self.document_viewer.setPlainText(f"Error reading file {path}: {e}")
        
    def open_text_context_menu(self, pos):
        """
        Adds assign and delete code segments functionally on
        right click in document viewer.
        """
        cursor = self.document_viewer.cursorForPosition(pos)
        char_pos = cursor.position()

        segment = self.repo.get_segment_at_position(self.current_document_id, char_pos)

        menu = self.document_viewer.createStandardContextMenu()

        # if segment is not None:
        #     segment_id = segment["id"]
        #     menu.addSeparator()
        #     delete = menu.addAction("Delete Highlight")
        #     delete.triggered.connect(
        #         lambda _checked=False, seg_id=segment_id: self.delete_segment_and_refresh(seg_id)
        #     )

        # cursor = self.document_viewer.textCursor()
        # if cursor.hasSelection():
        #     menu.addSeparator()
        #     assign = menu.addAction("Assign Code…")
        #     assign.triggered.connect(self.assign_code_to_selection)

        # menu.exec(self.document_viewer.mapToGlobal(pos))
    
    def clear_document(self):
        """
        Clear the viewer and reset current_document_id.
        """
        self.current_document_id = None
        self.document_viewer.clear()
        self.document_viewer.setText("Select a document to view its content.")

    def refresh_highlights(self):
        if self.current_document_id is None:
            return

        cursor = self.document_viewer.textCursor()
        cursor.select(QTextCursor.Document)
        default_format = QTextCharFormat()
        cursor.setCharFormat(default_format)

        rows = self.repo.get_coded_segments(self.current_document_id)
        log.debug("refresh_highlights: found %d segments", len(rows))

        for seg in rows:
            fmt = QTextCharFormat()

            # use the code color if present, otherwise a default
            code_color = seg["code_color"]
            if code_color:
                qcolor = QColor(code_color)
                if qcolor.isValid():
                    fmt.setBackground(qcolor)
                else:
                    fmt.setBackground(QColor("yellow"))
            else:
                fmt.setBackground(QColor("yellow"))

            cursor.setPosition(seg["start_offset"])
            cursor.setPosition(seg["end_offset"], QTextCursor.KeepAnchor)
            cursor.setCharFormat(fmt)