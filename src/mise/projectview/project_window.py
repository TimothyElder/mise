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

        main_layout = QVBoxLayout(self)

        splitter = QSplitter(self)
        main_layout.addWidget(splitter)

        # Left: File browser
        self.file_browser_widget = DocumentBrowserWidget(self.repo, self.texts_dir, self.project_root, parent=self)

        self.file_browser_widget.documentActivated.connect(self.on_document_activated)
        splitter.addWidget(self.file_browser_widget)

        # Center: Document viewer
        self.file_viewer_widget = DocumentViewerWidget(self.repo, parent=self)
        
        splitter.addWidget(self.file_viewer_widget)

        # Right: Code manager
        self.code_manager = CodeManager(
            repo=self.repo,
            parent=self
        )
        splitter.addWidget(self.code_manager)
        self.code_manager.codes_updated.connect(self.file_viewer_widget.refresh_highlights)
        splitter.setSizes([200, 600, 400])

    def on_document_activated(self, doc_id):
        self.file_viewer_widget.display_file_content(doc_id)
    
    def closeEvent(self, event):
        """
        Close database connection
        """
        if hasattr(self, "repo"):
            self.repo.close()
        super().closeEvent(event)