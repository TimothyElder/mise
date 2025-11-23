"""
Browser's job: detect clicks and emit high-level events.
It should not load files or know about the viewer at all.

Responsibility: everything to do with the left-hand side file/document list.

Move these into it:
    - State:
        - texts_dir
        - current_path
    - UI:
        - back_button
        - file_list
        - upload_button
    - Methods:
        - populate_file_list
        - go_back
        - handle_upload_clicked
        - open_file_context_menu
        - rename_document (UI piece only)
        - delete_document_from_ui (or better: emit signals and let ProjectWidget call repo)

And crucially, stop having this widget touch the repository directly where possible. Instead, give it a reference to a small interface:
    - Or inject ProjectRepository but restrict what it does.
        - Or, better, have it emit signals:
            - documentSelected(doc_id: int, path: Path)
            - documentRenamed(doc_id: int, new_name: str)
            - documentDeleted(doc_id: int)
"""

from PySide6.QtWidgets import (
    QSplitter, QVBoxLayout, QWidget, QListWidget,
    QTextBrowser, QPushButton, QListWidgetItem,
    QFileDialog, QMessageBox, QDialog, QMenu,
    QInputDialog, QWidget
)

from PySide6.QtGui import (
    QIcon, QTextCursor, QTextCharFormat, 
    QColor)

from PySide6.QtCore import Qt, Signal

from pathlib import Path

from ..utils.import_service import import_files

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# for cursor info
DOC_ID_ROLE = Qt.UserRole + 1
PATH_ROLE = Qt.UserRole + 2

def asset_path(name: str) -> str:
    return str(ASSETS_DIR / name)

class DocumentBrowserWidget(QWidget):
    documentActivated = Signal(str)  # path_str
    folderActivated = Signal(str)    # path_str

    def __init__(self, repo, texts_dir: Path, project_root: Path, parent=None):
        super().__init__(parent)
        
        # Config
        self.repo = repo
        self.texts_dir = texts_dir
        self.project_root = project_root

        # State
        self.current_path = self.texts_dir

        layout = QVBoxLayout(self)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)  # Initially disabled at root directory
        layout.addWidget(self.back_button)

        self.file_list = QListWidget()
        self.populate_file_list(self.current_path)
        layout.addWidget(self.file_list)

        # context menu for file list
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_file_context_menu)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.handle_upload_clicked)
        layout.addWidget(self.upload_button)

        self.file_list.itemClicked.connect(self.handle_item_click)
        
    def handle_item_click(self, item):
        """
        When clicking on items in the file browser emit path str if it is a file
        Refactor to use doc_id so it is managed by the database? 
        """

        path_str = item.data(PATH_ROLE)

        if not path_str:
            return  # Prevent None errors

        path_str = Path(path_str)

		# IF DIRECTORY
        if path_str.is_dir():
            self.current_path = path_str
            self.populate_file_list(self.current_path)
        # OTHERWISE IT IS FILE
        else:
            doc_id = self.repo.lookup_document_id(path_str)
            
            if doc_id is None:
                print(f"[WARN] File not registered in documents: {path_str}")
            
            self.current_document_id = doc_id
            
            print(f"doc_id from click is {doc_id}" )
            
            self.documentActivated.emit(path_str)

            # Now in ProjectWidget need to 
            
			
            




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
                    doc_id = None
                else:
                    doc = self.repo.get_document_by_text_path(child)
                    if doc is not None:
                        label = doc["display_name"]
                        doc_id = doc["id"]
                    else:
                        label = child.name
                        doc_id = None
                                                
                    icon = file_icon

                item = QListWidgetItem(label)
                item.setIcon(icon)
                item.setData(PATH_ROLE, str(child))   # always set path
                item.setData(DOC_ID_ROLE, doc_id)     # None for folders / unregistered
                self.file_list.addItem(item)

        except Exception as e:
            print(f"Error accessing directory {self.current_path}: {e}")

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