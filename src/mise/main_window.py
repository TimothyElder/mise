from pathlib import Path
import logging
log = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QInputDialog, QMessageBox
)
from PySide6.QtCore import QDir

from .utils.project_repository import ProjectRepository
from .projectview.project_window import ProjectView
from .project_init import create_project
from .analysisview.analysis_window import AnalysisWindow
from .widgets.welcome_widget import WelcomeWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Source Qualitative Data Analysis")
        self.resize(800, 600)

        # Create the menu bar
        self._create_menu_bar()

        # Set up the welcome widget
        welcome = WelcomeWidget()
        welcome.new_project_requested.connect(self._handle_create_new_project_requested)
        welcome.open_project_requested.connect(self._handle_open_project_requested)
        self.setCentralWidget(welcome)

    def _create_menu_bar(self):

        menu_bar = self.menuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")
        
        new_project = file_menu.addAction("Create New Project")
        new_project.triggered.connect(self._handle_create_new_project_requested)

        open_project = file_menu.addAction("Open Project")
        open_project.triggered.connect(self._handle_open_project_requested)

        help_menu = menu_bar.addMenu("Help")
        thing = help_menu.addAction("Some Help")
        

        view_menu = menu_bar.addMenu("View")
        switch_to_analysis = view_menu.addAction("Open Analysis")
        switch_to_analysis.triggered.connect(self._handle_open_analysis_requested)
        about_mise = view_menu.addAction("About Mise")
        about_mise.triggered.connect(self._handle_show_about_dialog)

    def _handle_open_analysis_requested(self):
        """
        Open Analyis window
        """
        
        if not hasattr(self, "_analysis_view"):
            self._analysis_view = AnalysisWindow()

        self.setCentralWidget(self._analysis_view)

    def _handle_create_new_project_requested(self):
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
            log.info("Project %s created at %r.", project_name, project_root)
            db_path = project_root / "project.db"
            repo = ProjectRepository(db_path)
            project = ProjectView(project_name, project_root, repo)
            self.setCentralWidget(project)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            log.error("Error creating project named %s at %r: %s", project_name, dirpath, e)

    def _handle_open_project_requested(self):
        """
        Open existing project from file dialog 
        """
        
        dirpath_str = QFileDialog.getExistingDirectory(
            self,
            "Select Mise Project Directory",
            QDir.homePath(),
            )
        if not dirpath_str:
            return  # user cancelled

        project_root = Path(dirpath_str)

        # Basic validation: must be a directory and look like a Mise project
        if not project_root.is_dir():
            QMessageBox.warning(self, "Invalid project", "The selected path is not a directory.")
            return

        # Require project.db and texts/ for now
        if not (project_root / "project.db").exists() or not (project_root / "texts").is_dir():
            QMessageBox.warning(
                self,
                "Invalid project",
                "The selected folder does not appear to be a Mise project.\n"
                "It should contain 'project.db' and a 'texts' directory."
            )
            return

        # Derive project_name from folder name, stripping .mise if present
        project_name = project_root.name
        if project_name.endswith(".mise"):
            project_name = project_name[:-5]

        db_path = project_root / "project.db"
        repo = ProjectRepository(db_path)

        # Swap the central widget to a ProjectView
        project = ProjectView(project_name, project_root, repo)
        self.setCentralWidget(project)

    def _handle_show_about_dialog(self):
        QMessageBox.about(
            self,
            "About Mise",
            "<b>Mise</b><br>"
            "An open-source qualitative data analysis tool.<br><br>"
            "Version 0.0.1<br>"
            "<a href='https://miseqda.com'>miseqda.com</a>"
        )