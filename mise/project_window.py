# Need redo the back button so that it just goes back one directory up the tree maybe some CLI thing for `cd ..`


from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QTextBrowser, QLabel, QListWidgetItem, QPushButton
from PySide6.QtGui import QIcon
import os


class ProjectWindow(QMainWindow):
    def __init__(self, project_name, project_path):
        super().__init__()
        self.setWindowTitle(f"Mise - {project_name}")
        self.resize(1200, 800)
        self.project_name = project_name
        self.project_path = project_path

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QHBoxLayout(central_widget)

        # Left: File list container with back button
        left_layout = QVBoxLayout()

        # Back Button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        left_layout.addWidget(self.back_button)

        # File List
        self.file_list = QListWidget()
        self.populate_file_list(project_path)  # Populate the file list
        left_layout.addWidget(self.file_list)

        main_layout.addLayout(left_layout)

        # Center: Document Viewer
        self.document_viewer = QTextBrowser()
        self.document_viewer.setText("Select a document to view its content.")  # Placeholder
        main_layout.addWidget(self.document_viewer)

        # Right: Code Manager
        self.code_manager = QLabel("Code Manager Placeholder")  # Replace with a real widget later
        main_layout.addWidget(self.code_manager)

        # Connect item click
        self.file_list.itemClicked.connect(self.handle_item_click)

    def populate_file_list(self, directory):
        """
        Populate the QListWidget with directories and files from the given directory.
        """
        self.file_list.clear()  # Clear the current list

        # Enable or disable the back button
        if directory == self.project_path:
            self.back_button.setDisabled(True)
        else:
            self.back_button.setDisabled(False)

        # Set icons
        folder_icon = QIcon(os.path.join(os.path.dirname(__file__), "assets", "folder.png"))
        file_icon = QIcon(os.path.join(os.path.dirname(__file__), "assets", "document.png"))

        try:
            items = os.listdir(directory)
            for item in sorted(items):
                full_path = os.path.join(directory, item)
                list_item = QListWidgetItem()
                list_item.setText(item)
                if os.path.isdir(full_path):
                    list_item.setIcon(folder_icon)  # Use folder icon
                else:
                    list_item.setIcon(file_icon)  # Use file icon
                self.file_list.addItem(list_item)
        except Exception as e:
            print(f"Error accessing directory {directory}: {e}")

    def handle_item_click(self, item):
        """
        Handle clicks on items in the file list.
        """
        item_name = item.text()
        full_path = os.path.join(self.project_path, item_name)

        if os.path.isdir(full_path):
            # If it's a directory, populate the list with its contents
            self.project_path = full_path  # Update project path to the subdirectory
            self.populate_file_list(full_path)
        else:
            # If it's a file, display its content in the document viewer
            self.display_file_content(full_path)

    def display_file_content(self, filepath):
        """
        Display the content of the selected file in the document viewer.
        """
        try:
            with open(filepath, "r") as f:
                content = f.read()
            self.document_viewer.setPlainText(content)  # Show content in plain text
        except Exception as e:
            self.document_viewer.setPlainText(f"Error reading file {filepath}: {e}")

    def go_back(self):
        """
        Navigate back to the parent directory.
        """
        parent_path = os.path.dirname(self.project_path)  # Get the parent directory
        if parent_path:  # Ensure it's valid
            self.project_path = parent_path
            self.populate_file_list(parent_path)