from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QInputDialog, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QDir

from pathlib import Path

from mise.project_window import ProjectWidget
from mise.project_init import create_project


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Source Qualitative Data Analysis")
        self.resize(800, 600)

        # Create the menu bar
        self._create_menu_bar()

        # Set up the welcome widget
        welcome = WelcomeWidget(on_new_project=self.create_new_project, on_open_project=self.open_project)
        self.setCentralWidget(welcome)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        self.setMenuBar(menu_bar)
        
        # You can add additional menu options later
        file_menu = menu_bar.addMenu("File")
        
        new_project = file_menu.addAction("Create New Project")
        new_project.triggered.connect(self.create_new_project)

        open_project = file_menu.addAction("Open Project")
        open_project.triggered.connect(self.open_project)
        
        about_menu = menu_bar.addMenu("About")

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
            project = ProjectWidget(project_name, project_root)
            self.setCentralWidget(project)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_project(self):
        # Let the user pick the *project root* (the .mise folder)
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

        # Swap the central widget to a ProjectWidget
        project = ProjectWidget(project_name, project_root)
        self.setCentralWidget(project)

class WelcomeWidget(QWidget):
    def __init__(self, on_new_project, on_open_project, parent=None):
        super().__init__(parent)
        
        self.on_new_project = on_new_project
        self.on_open_project = on_open_project

        # Set up layout
        layout = QHBoxLayout(self)

        # Left side: buttons for "Create New Project" and "Open Project"
        button_layout = QVBoxLayout()
        create_button = QPushButton("Create New Project")
        create_button.clicked.connect(self.on_new_project)
        open_button = QPushButton("Open Project")
        button_layout.addWidget(create_button)
        button_layout.addWidget(open_button)
        open_button.clicked.connect(self.on_open_project)
        button_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(button_layout)

        # Right side: logo and description
        logo_layout = QVBoxLayout()
        # Load the logo image
        logo_label = QLabel()
        pixmap = QPixmap("data/mise.png").scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # Add the logo to the layout
        layout.addWidget(logo_label)
        logo_label.setAlignment(Qt.AlignCenter)

        description_label = QLabel()
        description_label.setText(
            """<p style="font-size: 14px; color: grey;">Mise ("<em>meez</em>") is an qualitative data analysis tool designed to place good principles at the heart of software.</p>
               <p>There are a few principles that guide this software:</p>
               <ul>
                    <li>Codes should be applied to large chunks of text</li>
                    <li>Everything should be accessible to the analyst</li>
                    <li>Anlaysis should be made as transparent as possible</li>
               </ul>

                <p>Suggestions or bugs can be reported to <a href="mailto:timothy.b.elder@dartmouth.edu">Timothy.B.Elder@dartmouth.edu</a></p>

                <p><a href="https://miseqda.com">miseqda.com</a></p>
            """)
        description_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        description_label.setWordWrap(True)

        logo_layout.addWidget(description_label)
        layout.addLayout(logo_layout)