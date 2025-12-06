from pathlib import Path
import logging
logger = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QInputDialog, QMessageBox, QDialog, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QApplication
)
from PySide6.QtCore import QDir

from PySide6.QtGui import QAction, QKeySequence, QFont

from .widgets.welcome_widget import WelcomeWidget
from .widgets.report_dialog import CodeReportDialog
from .app_controller import AppController
from .ui import theme

from PySide6.QtGui import QFontDatabase


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.controller = AppController(self)
        self.controller.load_app_fonts()
        self._set_global_fonts()

        self._create_actions()
        self._create_menu_bar()

        self.setWindowTitle("Open Source Qualitative Data Analysis")
        self.resize(800, 600)

        # Set up the welcome widget
        welcome = WelcomeWidget()
        welcome.new_project_requested.connect(self._handle_create_new_project_requested)
        welcome.open_project_requested.connect(self._handle_open_project_requested)
        self.setCentralWidget(welcome)

    def _set_global_fonts(self):

        # Example: Inter as your app UI font
        ui_font = QFont(theme.FONT_SANS_FAMILY, pointSize=theme.CONTENT_FONT_SIZE_PT_DEFAULT)
        self.setFont(ui_font)

        # And if you want Qt’s default palette to assume this family:
        QApplication.setFont(ui_font)

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
            logger.error("Error creating project named %s at %r: %s", project_name, dirpath, e)
    
    def _create_actions(self):
        # File
        self.action_new_project = QAction("Create New Project", self)
        self.action_new_project.setShortcut(QKeySequence.New)
        self.action_new_project.triggered.connect(self._handle_create_new_project_requested)

        self.action_open_project = QAction("Open Project", self)
        self.action_open_project.setShortcut(QKeySequence.Open)
        self.action_open_project.triggered.connect(self._handle_open_project_requested)

        # View
        self.action_open_analysis = QAction("Open Analysis View", self)
        self.action_open_analysis.setShortcut("Ctrl+Shift+A")
        self.action_open_analysis.triggered.connect(self._handle_open_analysis_requested)

        self.action_open_project_view = QAction("Open Project View", self)
        self.action_open_project_view.setShortcut("Ctrl+Shift+P")
        self.action_open_project_view.triggered.connect(self._handle_project_view_requested)

        # Reports
        self.action_generate_report = QAction("Generate Code Report", self)
        self.action_generate_report.setShortcut("Ctrl+R")
        self.action_generate_report.triggered.connect(self._handle_generate_report_requested)

        # Help
        self.action_about = QAction("About Mise", self)
        self.action_about.triggered.connect(self._handle_show_about_dialog)

        self.action_show_shortcuts = QAction("Keyboard Shortcuts", self)
        self.action_show_shortcuts.triggered.connect(self._handle_show_shortcuts_dialog)

        # Font size
        self.action_increase_font = QAction("Increase Text Size", self)
        self.action_increase_font.setShortcut(QKeySequence.ZoomIn)
        self.action_increase_font.triggered.connect(self.controller.increase_text_size)

        self.action_decrease_font = QAction("Decrease Text Size", self)
        self.action_decrease_font.setShortcut(QKeySequence.ZoomOut)
        self.action_decrease_font.triggered.connect(self.controller.decrease_text_size)

        self.action_reset_font = QAction("Reset Text Size", self)
        self.action_reset_font.setShortcut("Ctrl+0")
        self.action_reset_font.triggered.connect(self.controller.reset_text_size)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        self.setMenuBar(menu_bar)

        # File
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_open_project)

        # View
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.action_open_analysis)
        view_menu.addAction(self.action_open_project_view)
        view_menu.addSeparator()
        view_menu.addAction(self.action_increase_font)
        view_menu.addAction(self.action_decrease_font)
        view_menu.addAction(self.action_reset_font)

        # Reports
        report_menu = menu_bar.addMenu("Reports")
        report_menu.addAction(self.action_generate_report)

        # Help
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.action_show_shortcuts)
        help_menu.addAction(self.action_about)

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
        print(project_root)

        self.controller.open_project(project_root = project_root, texts_dir = project_root / "texts" )

    def _handle_show_about_dialog(self):
        QMessageBox.about(
            self,
            "About Mise",
            "<b>Mise</b><br>"
            "An open-source qualitative data analysis tool.<br><br>"
            "Version 0.1.4<br>"
            "<a href='https://miseqda.com'>miseqda.com</a>"
        )

    def _handle_show_shortcuts_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")

        layout = QVBoxLayout(dialog)

        table = QTableWidget(dialog)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)

        # Collect the actions you actually want to show
        rows = [
            ("Create New Project", self.action_new_project),
            ("Open Project", self.action_open_project),
            ("Open Analysis View", self.action_open_analysis),
            ("Open Project View", self.action_open_project_view),
            ("Generate Code Report", self.action_generate_report),
            ("Increase Text Size", self.action_increase_font),
            ("Decrease Text Size", self.action_decrease_font),
            ("Reset Text Size", self.action_reset_font),
        ]

        table.setRowCount(len(rows))

        for row_idx, (label, action) in enumerate(rows):
            shortcut = action.shortcut().toString(QKeySequence.NativeText)
            table.setItem(row_idx, 0, QTableWidgetItem(label))
            table.setItem(row_idx, 1, QTableWidgetItem(shortcut))

        layout.addWidget(table)

        close_btn = QPushButton("Close", dialog)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.resize(500, 300)
        dialog.exec()