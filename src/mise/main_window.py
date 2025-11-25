from pathlib import Path
import logging
log = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QInputDialog, QMessageBox, QDialog
)
from PySide6.QtCore import QDir

from .widgets.welcome_widget import WelcomeWidget
from .widgets.report_dialog import CodeReportDialog
from .app_controller import AppController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.controller = AppController(self)

        self.setWindowTitle("Open Source Qualitative Data Analysis")
        self.resize(800, 600)

        # Create the menu bar
        self._create_menu_bar()

        # Set up the welcome widget
        welcome = WelcomeWidget()
        welcome.new_project_requested.connect(self._handle_create_new_project_requested)
        welcome.open_project_requested.connect(self._handle_open_project_requested)
        self.setCentralWidget(welcome)

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
            self.controller.create_project(project_name=project_name, base_dir=Path(dirpath))
            QMessageBox.information(self, "Success", f"Project '{project_name}' created successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            log.error("Error creating project named %s at %r: %s", project_name, dirpath, e)

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
        switch_to_analysis = view_menu.addAction("Open Analysis View")
        switch_to_analysis.triggered.connect(self._handle_open_analysis_requested)

        switch_to_project = view_menu.addAction("Open Project View")
        switch_to_project.triggered.connect(self._handle_project_view_requested)

        report_menu = menu_bar.addMenu("Reports")
        generate_code_report = report_menu.addAction("Generate Code Report")
        generate_code_report.triggered.connect(self._handle_generate_report_requested)

        about_mise = view_menu.addAction("About Mise")
        about_mise.triggered.connect(self._handle_show_about_dialog)

    def _handle_generate_report_requested(self):
        """
        Call report dialog and send results to app controller to generate html report
        """

        dialog = CodeReportDialog(self.controller.current_repo, self)
        if dialog.exec() != QDialog.Accepted:
            return

        code_ids = dialog.get_selected_code_ids()

        if not code_ids:
            QMessageBox.information(
                "No codes selected",
                "Please select at least one code to include in the report.",
            )
            return

        if self.controller.current_repo is None:
            QMessageBox.warning(
                "No project open",
                "Open a project before generating reports.",
            )
            return

        report_data = []

        for code_id in code_ids:
            meta = self.controller.current_repo.get_code_metadata(code_id)
            segments = self.controller.current_repo.get_segments_for_code(code_id)

            report_data.append({
                "code": meta,
                "segments": segments
            })        

        self.controller.generate_report(report_data)

    def _handle_open_analysis_requested(self):
        """
        Open Analysis window
        """
        self.controller.show_analysis_view()
    
    def _handle_project_view_requested(self):
        """
        Open Project Window
        """
        self.controller.show_project_view()

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

        self.controller.open_project(project_root = project_root)

    def _handle_show_about_dialog(self):
        QMessageBox.about(
            self,
            "About Mise",
            "<b>Mise</b><br>"
            "An open-source qualitative data analysis tool.<br><br>"
            "Version 0.0.1<br>"
            "<a href='https://miseqda.com'>miseqda.com</a>"
        )