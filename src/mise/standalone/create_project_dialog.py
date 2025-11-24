from PySide6.QtWidgets import (
    QWidget, QFileDialog, QInputDialog, QMessageBox, QDialog
)

from PySide6.QtCore import QDir

from mise.projectview.project_window import ProjectWidget
from project_init import create_project

import logging
log = logging.getLogger(__name__)

class CreateProjectDialog(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__()

    def create_new_project(self):
        """
        Calls function that creates project, using user defined project
        from file dialog box and sepcified project name.
        """
        dirpath = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for Project",
            QDir.homePath(),   # start in OS home directory
            )
        
        if not dirpath:
            return

        # Get the project name
        project_name, ok = QInputDialog.getText(self, "Project Name", "Enter a name for the project:")
        if not ok or not project_name:
            return

        # Create project directory
        try:
            project_root = create_project(project_name, dirpath)
            QMessageBox.information(self, "Success", f"Project '{project_name}' created successfully.")
            main_window = self.window()
            main_window.setCentralWidget(ProjectWidget(project_name, project_root))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
