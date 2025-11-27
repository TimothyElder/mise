"""
This handles bringing tpogether the different analysis widgets
including a code tree, document tree and then the multi use viewer
andn toolbar.
"""
from pathlib import Path
import logging
log = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QSplitter, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

from ..utils.project_repository import ProjectRepository
from .code_stats_tree import CodeStatsTreeWidget
from .document_stats_tree import DocumentStatsTreeWidget
from .analysis_document_viewer import AnalysisDocumentViewerWidget
from .code_viewer import CodeSegmentView  # you’ll create this

# write analysis helper scripts in the /analysis directory and make them accessible above including:
#   - tokenize text
#   - network functions
#   - word cloud

class AnalysisView(QWidget):

    PAGE_DOCUMENT = 0
    PAGE_CODE_SEGMENTS = 1

    def __init__(self, project_name: str, project_root: Path, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.project_root = project_root

        # Left: vertical splitter
        self.code_tree = CodeStatsTreeWidget(repo=self.repo, parent=self)
        self.document_tree = DocumentStatsTreeWidget(repo=self.repo, parent=self)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.code_tree)
        left_splitter.addWidget(self.document_tree)
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 1)

        # Style: visible handle + resize cursor
        left_splitter.setHandleWidth(6)
        left_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dddddd;
            }
            QSplitter::handle:vertical {
                margin: 0px;
                cursor: splitVCursor;  /* up-down arrows */
            }
        """)

        # ----- Right side: stacked widget (document view vs code segments) -----
        self.document_view = AnalysisDocumentViewerWidget(repo, self)
        self.code_segment_view = CodeSegmentView(repo, self)

        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.document_view)      # PAGE_DOCUMENT
        self.stacked.addWidget(self.code_segment_view)  # PAGE_CODE_SEGMENTS

        # Default: show document
        self.stacked.setCurrentIndex(self.PAGE_DOCUMENT)

        # ----- Main horizontal splitter -----
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.stacked)
        main_splitter.setStretchFactor(0, 0)  # left narrower
        main_splitter.setStretchFactor(1, 1)  # right grows

        # Style: visible handle + resize cursor
        main_splitter.setHandleWidth(6)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dddddd;
            }
            QSplitter::handle:horizontal {
                margin: 0px;
                cursor: splitHCursor;  /* left-right arrows */
            }
        """)

        # ----- Top-level layout -----
        layout = QHBoxLayout(self)
        layout.addWidget(main_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Later: wire up signals
        self._connect_signals()

    def _connect_signals(self):
        """
        Hook up interactions:
        - selecting a document in the document tree loads it in document_view
        - selecting a code switches stacked widget to code segments, etc.
        """
        # Example / placeholder; adapt to your actual signal API.

        # Document tree -> show document view
        self.document_tree.documentSelected.connect(self._on_document_selected)

        # Code tree -> show code segments view
        self.code_tree.codeSelected.connect(self._on_code_selected)

        self.code_segment_view.segmentActivated.connect(self._on_segment_activated)

    def show_document_page(self):
        self.stacked.setCurrentIndex(self.PAGE_DOCUMENT)

    def show_code_segments_page(self):
        self.stacked.setCurrentIndex(self.PAGE_CODE_SEGMENTS)

    def _on_document_selected(self, text_path: str, doc_id: int):
        # text_path is the DB value (now relative); resolve it to an absolute path
        abs_path = (self.repo.texts_dir / text_path).resolve()

        self.show_document_page()
        self.document_view.display_file_content(abs_path)
        self.document_view.current_document_id = doc_id
        self.document_view.refresh_highlights()

    def _on_code_selected(self, code_id: int):
        self.show_code_segments_page()
        self.code_segment_view.load_segments_for_code(code_id)
    
    def _on_segment_activated(self, doc_id: int, start: int, end: int):
        # Switch to document page
        self.show_document_page()
        path = self.repo.get_document_path(doc_id)

        self.document_view.display_file_content(path)
        self.document_view.current_document_id = doc_id

        # Highlight all segments
        self.document_view.refresh_highlights()

        # Focus this specific segment
        cursor = self.document_view.document_viewer.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.document_view.document_viewer.setTextCursor(cursor)
        self.document_view.document_viewer.ensureCursorVisible()