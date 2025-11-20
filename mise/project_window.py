from PySide6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget, QListWidget, QTextBrowser, QLabel, QPushButton, QListWidgetItem, QFileDialog, QMessageBox
from PySide6.QtGui import QIcon
from pathlib import Path
import os

from mise.code_manager import CodeManager
from mise.utils.file_io import convert_to_canonical_text



# Allowed file types to upload
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".md", ".markdown"}


class ProjectWindow(QMainWindow):
    def __init__(self, project_name, project_root):
        super().__init__()
        self.setWindowTitle(f"Mise - {project_name}")
        self.resize(1200, 800)

        # Store paths
        self.project_name = project_name
        self.project_root = Path(project_root)
        self.current_path = self.project_root
        self.texts_dir = self.project_root / "texts"

        # Main widget
        splitter = QSplitter()
        self.setCentralWidget(splitter)

        # Left: File list with back button
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)  # Initially disabled at root directory
        left_layout.addWidget(self.back_button)

        self.file_list = QListWidget()
        # Use current_path (or project_root) instead of undefined project_root
        self.populate_file_list(self.current_path)
        left_layout.addWidget(self.file_list)

        splitter.addWidget(left_widget)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.handle_upload_clicked)
        left_layout.addWidget(self.upload_button)

        # Center: Document viewer
        self.document_viewer = QTextBrowser()
        self.document_viewer.setText("Select a document to view its content.")
        splitter.addWidget(self.document_viewer)

        # Right: Code manager
        self.code_manager = QLabel("Code Manager Placeholder")
        splitter.addWidget(self.code_manager)

        splitter.setSizes([200, 600, 400])

        self.file_list.itemClicked.connect(self.handle_item_click)

    def populate_file_list(self, directory):
        """
        Populate the QListWidget with directories and files from the given directory.
        """
        self.file_list.clear()  # Clear the current list

        # Enable or disable the back button based on directory
        self.back_button.setEnabled(os.path.abspath(directory) != self.project_root)

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
        full_path = os.path.join(self.texts_dir, item_name)

        if os.path.isdir(full_path):
            # If it's a directory, populate the list with its contents
            self.project_root = full_path  # Update project path to the subdirectory
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
        Navigate back to the parent directory, emulating 'cd ..' behavior.
        """
        parent_path = os.path.dirname(self.project_root)  # Get the parent directory

        # Ensure we don't navigate above the root project directory
        if os.path.abspath(parent_path) != os.path.abspath(self.project_root):
            self.project_root = parent_path
            self.populate_file_list(parent_path)

    def handle_upload_clicked(self):
        # 1) Open dialog for multiple files
        dialog_filter = (
            "Documents (*.pdf *.docx *.doc *.md *.markdown);;"
            "All Files (*)"
        )
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select documents to import",
            "",                # start dir; you can use last-used dir later
            dialog_filter,
        )
        if not file_paths:
            return  # user cancelled

        # 2) Process each file
        imported_any = False
        errors = []

        for src in file_paths:
            src_path = Path(src)
            ext = src_path.suffix.lower()

            if ext not in ALLOWED_EXTENSIONS:
                errors.append(f"{src_path.name}: unsupported extension '{ext}'")
                continue

            try:
                text = convert_to_canonical_text(src_path)    # we'll define this below
                dest_path = self._allocate_text_path(src_path)
                dest_path.write_text(text, encoding="utf-8")

                # TODO: insert a row in documents table here later

                imported_any = True
            except Exception as e:
                errors.append(f"{src_path.name}: {e}")

        # 3) Feedback + refresh view
        if imported_any:
            # however you show files – maybe list contents of self.texts_dir
            self.populate_file_list(self.texts_dir)

        if errors:
            QMessageBox.warning(
                self,
                "Import issues",
                "Some files could not be imported:\n\n" + "\n".join(errors),
            )

    def _allocate_text_path(self, src_path: Path) -> Path:
        """
        Decide how to name canonical text files in texts/.
        For now: doc-N.txt, independent of original filename.
        """
        # Very naive incremental scheme – good enough for now
        # Later you will want this tied to a documents table (ID → filename).
        existing = list(self.texts_dir.glob("doc-*.txt"))
        next_id = len(existing) + 1
        return self.texts_dir / f"doc-{next_id:04d}.txt"