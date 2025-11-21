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

from mise.utils.import_service import import_files
from mise.utils.project_repository import ProjectRepository
from mise.code_manager import CodeManager
from mise.code_picker import CodePickerDialog

# write analysis helper scripts in the /analysis directory and make them accessible above including:
#   - tokenize text
#   - network functions
#   - word cloud

class AnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QGridLayout()

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


