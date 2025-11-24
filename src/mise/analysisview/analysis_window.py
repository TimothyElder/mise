"""
This handles bringing tpogether the different analysis widgets
including a code tree, document tree and then the multi use viewer
andn toolbar.
"""

from PySide6.QtWidgets import (
    QSplitter, QVBoxLayout, QWidget, QListWidget,
    QTextBrowser, QPushButton, QListWidgetItem,
    QFileDialog, QMessageBox, QDialog, QGridLayout
)

from PySide6.QtGui import (
    QIcon, QTextCursor, QTextCharFormat, 
    QColor)

from PySide6.QtCore import Qt

from pathlib import Path

from mise.utils.project_repository import ProjectRepository


# write analysis helper scripts in the /analysis directory and make them accessible above including:
#   - tokenize text
#   - network functions
#   - word cloud

class AnalysisWidget(QWidget):
    def __init__(self, project_name, project_root):
        super().__init__()

        # Config
        self.project_name = project_name
        self.project_root = Path(project_root)
        self.texts_dir = self.project_root / "texts"

       # Open Database connection via repository
        self.db_path = self.project_root / "project.db"
        self.repo = ProjectRepository(self.db_path)


        # State
        current_document_id = None
        current_path = None
        current_segment_id  = None
        current_code_id = None

        main_layout = QGridLayout(self)

        # Include call to connect to repository so information can be pulled in
        # self.repo.....

        # add layouts for:
        #    • AnalysisWidget with:
        #       • left QSplitter:
        #           • CodeTreeWidget
        #           • DocumentTreeWidget
        #       • right QStackedWidget:
        #           • DocumentView
        #           • CodeSegmentView

        # need to create toolbar with some function calls

        # When code selected show ssegments need to make this
        self.code_manager.code_selected.connect(self.show_segments_for_code)


