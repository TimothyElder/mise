from pathlib import Path
import logging
log = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QSplitter, QVBoxLayout, QWidget
)

from PySide6.QtCore import Qt

from ..utils.project_repository import ProjectRepository
from .code_browser import CodeBrowserWidget
from .document_browser import DocumentBrowserWidget
from .document_viewer import DocumentViewerWidget

class ProjectView(QWidget):

    def __init__(self, project_name, project_root, repo: ProjectRepository):
        super().__init__()

        log.info("Opened ProjectView for %s at %r", project_name, project_root)

        # Config
        self.project_name = project_name
        self.project_root = Path(project_root)
        self.texts_dir = self.project_root / "texts"
        self.repo = repo

        splitter = QSplitter(Qt.Horizontal, self)

        # Margins: let the splitter use full space
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(splitter)

        splitter.setHandleWidth(6)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dddddd;
            }
            QSplitter::handle:horizontal {
                margin: 0px;
                cursor: splitHCursor;  /* left-right arrows */
            }
        """)


        # Let splitter own the children (no need to pass parent=self here)
        self.file_browser_widget = DocumentBrowserWidget(self.repo, self.texts_dir, self.project_root)
        self.file_viewer_widget = DocumentViewerWidget(self.repo)
        self.code_browser_widget = CodeBrowserWidget(repo=self.repo)

        splitter.addWidget(self.file_browser_widget)
        splitter.addWidget(self.file_viewer_widget)
        splitter.addWidget(self.code_browser_widget)

        splitter.setStretchFactor(0, 1)  # browser
        splitter.setStretchFactor(1, 2)  # viewer
        splitter.setStretchFactor(2, 1)  # codes
        
        self.file_browser_widget.document_activated.connect(self.on_document_activated)
        self.file_browser_widget.document_deleted.connect(self.on_document_deleted)
        self.file_browser_widget.document_renamed.connect(self.on_document_renamed)
        self.file_browser_widget.memo_view_requested.connect(self.open_memo_view_for_document)
        self.code_browser_widget.codes_updated.connect(self.file_viewer_widget.refresh_highlights)
        # self.code_browser_widget.code_deleted.connect(self.on_code_deleted)

    def debug_state(self):
        """
        debug sentinel
        """
        print("Browser:", self.file_browser_widget.current_path)
        print("Project:", self.current_document_id)
        print("Viewer:", self.file_viewer_widget.current_document_id)

    def on_document_deleted(self, doc_id: int, text_path: str):
        if self.file_viewer_widget.current_document_id == doc_id:
            self.file_viewer_widget.clear_document()
            log.info("Deleted active document_id=%s (path=%r)", doc_id, text_path)

    def open_memo_view_for_document(self):
        raise ValueError("Memo view Not yet implemented")

    def on_document_renamed(self, doc_id: int, new_name: str):
        if self.file_viewer_widget.current_document_id == doc_id:
            self.setWindowTitle(f"Mise — {new_name}")
            log.info("Renamed active document_id=%s to %r", doc_id, new_name)
        
    def on_document_activated(self, path: Path):
        # Ensure we always work with Path inside
        path = Path(path)

        # Look up document id for this path
        doc_id = self.repo.lookup_document_id(path)
        if doc_id is None:
            log.warning("No document id for path %r", path)
        else:
            log.info("Activated document_id=%s for %r", doc_id, path)

        # Push state into the viewer
        self.file_viewer_widget.current_document_id = doc_id

        # Show content and refresh highlights for that doc
        self.file_viewer_widget.display_file_content(path)
        self.file_viewer_widget.refresh_highlights()
    
    def closeEvent(self, event):
        """
        Close database connection
        """
        if hasattr(self, "repo"):
            self.repo.close()
        super().closeEvent(event)