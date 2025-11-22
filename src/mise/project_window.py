"""
project_window.py

Manages the project screen where documents are imported and viewed
and codes applied.
"""

from PySide6.QtWidgets import (
    QSplitter, QVBoxLayout, QWidget, QListWidget,
    QTextBrowser, QPushButton, QListWidgetItem,
    QFileDialog, QMessageBox, QDialog, QMenu,
    QInputDialog
)

from PySide6.QtGui import (
    QIcon, QTextCursor, QTextCharFormat, 
    QColor)

from PySide6.QtCore import Qt

from pathlib import Path

from .utils.import_service import import_files
from .utils.project_repository import ProjectRepository
from .code_manager import CodeManager
from .code_picker import CodePickerDialog

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# for cursor info
DOC_ID_ROLE = Qt.UserRole + 1
PATH_ROLE = Qt.UserRole + 2

def asset_path(name: str) -> str:
    return str(ASSETS_DIR / name)

class ProjectWidget(QWidget):
    
    def __init__(self, project_name, project_root):
        super().__init__()

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

        main_layout = QVBoxLayout(self)

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

        # context menu for file list
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_file_context_menu)

        splitter.addWidget(left_widget)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.handle_upload_clicked)
        left_layout.addWidget(self.upload_button)

        # Center: Document viewer
        self.document_viewer = QTextBrowser()
        self.document_viewer.setText("Select a document to view its content.")
        splitter.addWidget(self.document_viewer)

        # context menu for document viewer
        self.document_viewer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.document_viewer.customContextMenuRequested.connect(self.open_text_context_menu)

        # Right: Code manager
        self.code_manager = CodeManager(
            repo=self.repo,
            parent=self
        )
        splitter.addWidget(self.code_manager)
        self.code_manager.codes_updated.connect(self.refresh_highlights)
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

        folder_icon = QIcon(asset_path("folder.png"))
        file_icon = QIcon(asset_path("document.png"))

        try:
            # Sort: folders first, then files, both alphabetically
            children = sorted(
                self.current_path.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
            for child in children:
                if child.is_dir():
                    label = child.name
                    icon = folder_icon
                else:
                    doc = self.repo.get_document_by_text_path(child)

                    if doc is not None:
                        label = doc["display_name"]
                        doc_id = doc["id"]
                    else:
                        label = child.name
                        doc_id = None

                    list_item = QListWidgetItem(label)
                    list_item.setIcon(file_icon)
                    list_item.setData(PATH_ROLE, str(child))
                    list_item.setData(DOC_ID_ROLE, doc_id)
                    
                    icon = file_icon

                list_item = QListWidgetItem(label)
                list_item.setIcon(icon)
                
                list_item.setData(PATH_ROLE, str(child)) # store the document ID instead of the file path
                list_item.setData(DOC_ID_ROLE, doc_id) # store text path
                self.file_list.addItem(list_item)
        except Exception as e:
            print(f"Error accessing directory {self.current_path}: {e}")


    def handle_item_click(self, item):
        path_str = item.data(PATH_ROLE)

        if not path_str:
            return  # Prevent None errors

        path_str = Path(path_str)

        if path_str.is_dir():
            self.current_path = path_str
            self.populate_file_list(self.current_path)
        else:
            doc_id = self.repo.lookup_document_id(path_str)

            if doc_id is None:
                print(f"[WARN] File not registered in documents: {path_str}")
            self.current_document_id = doc_id
            print(f"doc_id from click is {doc_id}" )

            self.display_file_content(path_str)

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

    def open_file_context_menu(self, pos):
        """
        File list context menu for deleting and renaming files.
        """
            # pos is in file_list's coordinate system
        item = self.file_list.itemAt(pos)
        if item is None:
            return  # right-clicked on empty space, ignore or show generic menu
        
        doc_id = item.data(DOC_ID_ROLE)
        if doc_id is None:
            return  # not a registered document

        menu = QMenu(self)

        open_action = menu.addAction("Open Document in Memo View")
        # assign.triggered.connect(self.open_document_in_memo_view)
        rename_action = menu.addAction("Rename")
        remove_action = menu.addAction("Remove from project")
        
        action = menu.exec(self.file_list.mapToGlobal(pos))

        if action == open_action:
            # stub
            raise ValueError("Document open is not yet implemented.")
        elif action == rename_action:
            self.rename_document(item, doc_id)
        elif action == remove_action:
            self.delete_document_from_ui(item, doc_id)
    
    def open_text_context_menu(self, pos):
        """
        Adds assign and delete code segments functionally on
        right click in document viewer.
        """
        cursor = self.document_viewer.cursorForPosition(pos)
        char_pos = cursor.position()

        segment = self.repo.get_segment_at_position(self.current_document_id, char_pos)

        menu = self.document_viewer.createStandardContextMenu()

        if segment is not None:
            segment_id = segment["id"]
            menu.addSeparator()
            delete = menu.addAction("Delete Highlight")
            delete.triggered.connect(
                lambda _checked=False, seg_id=segment_id: self.delete_segment_and_refresh(seg_id)
            )

        cursor = self.document_viewer.textCursor()
        if cursor.hasSelection():
            menu.addSeparator()
            assign = menu.addAction("Assign Code…")
            assign.triggered.connect(self.assign_code_to_selection)

        menu.exec(self.document_viewer.mapToGlobal(pos))
    
    def delete_segment_and_refresh(self, segment_id):
        self.repo.delete_segment(segment_id)
        self.refresh_highlights()
    
    def rename_document(self, item: QListWidgetItem, doc_id: int):
        current_name = item.text()

        new_name, ok = QInputDialog.getText(
            self,
            "Rename document",
            "New name:",
            text=current_name,
        )
        if not ok:
            return

        new_name = new_name.strip()
        if not new_name or new_name == current_name:
            return

        rows = self.repo.rename_document_db(new_name, doc_id)
        if rows:
            item.setText(new_name)

    def delete_document_from_ui(self, item, doc_id: int):
        rows, text_path = self.repo.delete_document(doc_id)
        print(f"[UI] repo deleted {rows} document(s) for id={doc_id}, path={text_path!r}")

        if rows:
            # 1) Remove file from disk
            if text_path:
                try:
                    Path(text_path).unlink(missing_ok=True)
                except Exception as e:
                    print(f"[WARN] Failed to delete file {text_path}: {e}")

            # 2) Remove the item from the list
            row_index = self.file_list.row(item)
            self.file_list.takeItem(row_index)

            # optional: refresh highlights, clear current_document_id if needed
            if self.current_document_id == doc_id:
                self.current_document_id = None
                self.document_viewer.clear()
                self.refresh_highlights()
        else:
            print(f"[WARN] No document deleted for id {doc_id}")
        

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