"""
project_window.py

ProjectWidget should be more like:
	- Build the splitter and layout.
	- Construct:
	    - DocumentBrowserWidget
	    - DocumentViewerWidget
	    - CodeManager
	- Connect signals:
	    - From browser → viewer (documentSelected → load doc and set current_document_id).
	    - From code manager / viewer → repository updates.

The only methods that should remain here are:
	- __init__
	- closeEvent
	- A few small glue handlers (like “when doc changes, update viewer & highlights”).

Right now you're putting all logic in here, and it's not sustainable.

Need to Name state consistently and have ProjectWidget control it. 
	- current_document_id
	- current_path
	- current_segment_id (if needed)
	- current_code_id (if ever needed)
"""

from PySide6.QtWidgets import (
    QSplitter, QVBoxLayout, QWidget, QListWidget,
    QTextBrowser, QPushButton, QListWidgetItem,
    QFileDialog, QMessageBox, QDialog, QMenu,
    QInputDialog
)

from PySide6.QtGui import (
    QIcon, QTextCursor, QTextCharFormat, 
    QColor)

from PySide6.QtCore import Qt

from pathlib import Path

from ..utils.import_service import import_files
from ..utils.project_repository import ProjectRepository
from .code_manager import CodeManager
from .code_picker import CodePickerDialog
from .document_browser import DocumentBrowserWidget
from .document_viewer import DocumentViewerWidget

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# for cursor info
DOC_ID_ROLE = Qt.UserRole + 1
PATH_ROLE = Qt.UserRole + 2

def asset_path(name: str) -> str:
    return str(ASSETS_DIR / name)

class ProjectWidget(QWidget):

    """
    Okay I am starting to understand this now, which is that when a class that is imported from another 
    file is included in the init of the parent class, it is essentially saying create an instance of that
    class here and make its methods available. So that is sort of the difference between an instance and 
    a class. A class is the generic description of the capabilities and functions of some unit of python
    and then the instance is a specific well instance for lack of a better word.

    More specifically in the init of the ProjectWidget class, declaring:

    self.viewer = DocumentViewerWidget(repo=self.repo, parent=self)

    is telling the program to create a speecific object that abides by the blueprint declared by 
    DocumentViewerWidget. And then it can be invoked by self.viewer.load_document for example. And
    the syntax of that name is illuminating because self is saying, this instance object viewer that 
    follows the blueprint and then the specific function 
    """

    def __init__(self, project_name, project_root):
        super().__init__()


        self.project_name = project_name
        self.project_root = Path(project_root)
        self.texts_dir = self.project_root / "texts"

       # Open Database connection via repository
        self.db_path = self.project_root / "project.db"
        self.repo = ProjectRepository(self.db_path)

        splitter = QSplitter(Qt.Horizontal, self)  # be explicit

        # Margins: let the splitter use full space
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(splitter)

                # Make the handle thicker and visually distinct
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
        self.code_manager = CodeManager(repo=self.repo)

        splitter.addWidget(self.file_browser_widget)
        splitter.addWidget(self.file_viewer_widget)
        splitter.addWidget(self.code_manager)

        # Optional: stretch factors instead of magic sizes
        splitter.setStretchFactor(0, 1)  # browser
        splitter.setStretchFactor(1, 2)  # viewer
        splitter.setStretchFactor(2, 1)  # codes
        
        self.file_browser_widget.documentActivated.connect(self.on_document_activated)
        self.code_manager.codes_updated.connect(self.file_viewer_widget.refresh_highlights)

    def debug_state(self):
        """
        debug sentinel
        """

        print("Browser:", self.file_browser_widget.current_path)
        print("Project:", self.current_document_id)
        print("Viewer:", self.file_viewer_widget.current_document_id)
        
    def on_document_activated(self, path: Path):
        # Ensure we always work with Path inside
        path = Path(path)

        # Look up document id for this path
        doc_id = self.repo.lookup_document_id(path)
        if doc_id is None:
            print(f"[WARN] No document id for path {path}")
        else:
            print(f"[INFO] Activated document id {doc_id} for {path}")

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