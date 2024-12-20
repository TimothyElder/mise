from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QInputDialog, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import os

from mise.project_manager import create_project_directory
from mise.project_window import ProjectWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Source Qualitative Data Analysis")
        self.resize(800, 600)

        # Create the menu bar
        self._create_menu_bar()

        # Set up the welcome widget
        self.welcome_widget = WelcomeWidget()
        self.setCentralWidget(self.welcome_widget)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        self.setMenuBar(menu_bar)
        # You can add additional menu options later
        file_menu = menu_bar.addMenu("File")
        about_menu = menu_bar.addMenu("About")

class WelcomeWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up layout
        layout = QHBoxLayout(self)

        # Left side: buttons for "Create New Project" and "Open Project"
        button_layout = QVBoxLayout()
        create_button = QPushButton("Create New Project")
        create_button.clicked.connect(self.create_new_project)
        open_button = QPushButton("Open Project")
        button_layout.addWidget(create_button)
        button_layout.addWidget(open_button)
        open_button.clicked.connect(self.open_project)
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
            """)
        description_label.setAlignment(Qt.AlignLeft)
        description_label.setWordWrap(True)

        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(description_label)
        layout.addLayout(logo_layout)

    def create_new_project(self):
    # Get the directory
        dirpath = QFileDialog.getExistingDirectory(self, "Select Directory for Project")
        if not dirpath:
            return

        # Get the project name
        project_name, ok = QInputDialog.getText(self, "Project Name", "Enter a name for the project:")
        if not ok or not project_name:
            return

        # Attempt to create the project directory
        try:
            create_project_directory(project_name, dirpath)
            QMessageBox.information(self, "Success", f"Project '{project_name}' created successfully.")

            # Open ProjectWindow
            self.parent().setCentralWidget(ProjectWindow(project_name, dirpath))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_project(self):
        dirpath = QFileDialog.getExistingDirectory(self, "Select Directory for Project")


        print(type(dirpath))
        print(type(os.path.basename(dirpath)))
        if not dirpath:
            return
        
        # THis is broken as the ProjectWindow Class was designed only with new projects in mind:
        # TypeError: ProjectWindow.__init__() missing 1 required positional argument: 'project_path'
        self.parent().setCentralWidget(ProjectWindow(os.path.basename(dirpath), dirpath))