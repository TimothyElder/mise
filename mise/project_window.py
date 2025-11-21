from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QVBoxLayout, QWidget, QListWidget,
    QTextBrowser, QPushButton, QListWidgetItem, QApplication,
    QFileDialog, QMessageBox, QDialog
)

from PySide6.QtGui import (
    QIcon, QTextCursor, QTextCharFormat, 
    QColor, QKeySequence, QAction)

from PySide6.QtCore import Qt

from pathlib import Path

from mise.utils.import_service import import_files
from mise.utils.project_repository import ProjectRepository
from mise.code_manager import CodeManager
from mise.code_picker import CodePickerDialog

class ProjectWidget(QWidget):
    def __init__(self, project_name, project_root):
        super().__init__()
        self.setWindowTitle(f"Mise - {project_name}")
        self.resize(1200, 800)

        # State
        self.current_document_id = None

        # Paths
        self.project_name = project_name
        self.project_root = Path(project_root)
        self.texts_dir = self.project_root / "texts"
        self.current_path = self.texts_dir

       # Open Database connection via repository
        self.db_path = self.project_root / "project.db"
        self.repo = ProjectRepository(self.db_path)

        # Top-level layout on this widget
        main_layout = QVBoxLayout(self)

        # The splitter is now just a child widget
        splitter = QSplitter(self)
        main_layout.addWidget(splitter)

        # Left: File list with back button
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)  # Initially disabled at root directory
        left_layout.addWidget(self.back_button)

        self.file_list = QListWidget()
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

        self.document_viewer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.document_viewer.customContextMenuRequested.connect(self.open_text_context_menu)

        # Right: Code manager
        self.code_manager = CodeManager(self.repo)
        splitter.addWidget(self.code_manager)
        splitter.setSizes([200, 600, 400])

        self.file_list.itemClicked.connect(self.handle_item_click)

    def populate_file_list(self, directory: Path):
        """
        Populate the QListWidget with directories and files from the given directory.
        `directory` is a Path.
        """
        directory = Path(directory)
        self.current_path = directory

        self.file_list.clear()

        # Enable or disable the back button based on directory
        self.back_button.setEnabled(self.current_path != self.project_root)

        # Set icons
        assets_dir = Path(__file__).resolve().parent / "assets"
        folder_icon = QIcon(str(assets_dir / "folder.png"))
        file_icon = QIcon(str(assets_dir / "document.png"))

        try:
            # Sort: folders first, then files, both alphabetically
            children = sorted(
                self.current_path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
            for child in children:
                list_item = QListWidgetItem(child.name)
                if child.is_dir():
                    list_item.setIcon(folder_icon)
                else:
                    list_item.setIcon(file_icon)

                # Store full path on the item for later use
                list_item.setData(Qt.UserRole, str(child))

                self.file_list.addItem(list_item)
        except Exception as e:
            print(f"Error accessing directory {self.current_path}: {e}")


    def handle_item_click(self, item):
        full_path = Path(item.data(Qt.UserRole))

        if full_path.is_dir():
            self.current_path = full_path
            self.populate_file_list(self.current_path)
        else:
            doc_id = self.repo.lookup_document_id(full_path)
            if doc_id is None:
                print(f"[WARN] File not registered in documents: {full_path}")
            self.current_document_id = doc_id

            self.display_file_content(full_path)

        self.refresh_highlights()

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
        Navigate back to the parent directory, but never above project_root.
        """
        if self.current_path == self.project_root:
            return  # already at root, nothing to do

        parent = self.current_path.parent

        # Only allow going back within the project tree
        if parent == self.project_root or self.project_root in parent.parents:
            self.populate_file_list(parent)

    def handle_upload_clicked(self):
        dialog_filter = (
            "Documents (*.pdf *.docx *.doc *.md *.markdown);;"
            "All Files (*)"
        )
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select documents to import",
            "",
            dialog_filter,
        )
        if not file_paths:
            return  # user cancelled

        src_paths = [Path(src) for src in file_paths]
        imported_any, errors = import_files(src_paths, self.texts_dir, self.repo)

        if imported_any:
            self.populate_file_list(self.texts_dir)

        if errors:
            QMessageBox.warning(
                self,
                "Import issues",
                "Some files could not be imported:\n\n" + "\n".join(errors),
            )
    
    def closeEvent(self, event):
        """
        Close database connection
        """
        if hasattr(self, "repo"):
            self.repo.close()
        super().closeEvent(event)
    
    def open_text_context_menu(self, pos):
        """
        Adds assign code functionally on right click in document viewer"""
        menu = self.document_viewer.createStandardContextMenu()

        cursor = self.document_viewer.textCursor()
        if cursor.hasSelection():
            menu.addSeparator()
            assign = menu.addAction("Assign Code…")
            assign.triggered.connect(self.assign_code_to_selection)

        menu.exec(self.document_viewer.mapToGlobal(pos))

    def assign_code_to_selection(self):
        """
        Assign code to segment of text
        """
        if self.current_document_id is None:
            return

        cursor = self.document_viewer.textCursor()
        if not cursor.hasSelection():
            return

        dialog = CodePickerDialog(self.repo.connection, self)
        if dialog.exec() != QDialog.Accepted:
            return

        code_id = dialog.get_code_id()
        if code_id is None:
            return

        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        self.repo.add_coded_segment(
            document_id=self.current_document_id,
            code_id=code_id,
            start_offset=start,
            end_offset=end,
            memo=None,  # or hook up a memo dialog later
        )

        self.refresh_highlights()

    def refresh_highlights(self):
        if self.current_document_id is None:
            return

        cursor = self.document_viewer.textCursor()
        cursor.select(QTextCursor.Document)
        default_format = QTextCharFormat()
        cursor.setCharFormat(default_format)

        rows = self.repo.get_coded_segments(self.current_document_id)
        print("refresh_highlights: found", len(rows), "segments")  # keep or drop

        for seg in rows:
            fmt = QTextCharFormat()

            # use the code color if present, otherwise a default
            code_color = seg["code_color"]
            if code_color:
                qcolor = QColor(code_color)
                if qcolor.isValid():
                    fmt.setBackground(qcolor)
                else:
                    fmt.setBackground(QColor("yellow"))
            else:
                fmt.setBackground(QColor("yellow"))

            cursor.setPosition(seg["start_offset"])
            cursor.setPosition(seg["end_offset"], QTextCursor.KeepAnchor)
            cursor.setCharFormat(fmt)