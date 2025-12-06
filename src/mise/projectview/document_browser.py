import logging
logger = logging.getLogger(__name__)
from pathlib import Path

from PySide6.QtWidgets import (
    QVBoxLayout, QWidget, QListWidget,
    QPushButton, QListWidgetItem, QFileDialog,
    QMessageBox, QMenu, QInputDialog
)
from PySide6.QtGui import (
    QIcon)
from PySide6.QtCore import Qt, Signal

from ..utils.import_service import import_files
from ..utils.paths import asset_path

# for cursor info
DOC_ID_ROLE = Qt.UserRole + 1
PATH_ROLE = Qt.UserRole + 2

class DocumentBrowserWidget(QWidget):
    document_activated = Signal(object)  # path
    folder_activated = Signal(str)       # path

    document_deleted = Signal(int, str)    # doc_id, text_path
    document_renamed = Signal(int, str)    # doc_id, new_name
    memo_view_requested = Signal(int)     # doc_id

    def __init__(self, repo, texts_dir: Path, project_root: Path, parent=None):
        super().__init__(parent)
        
        # Config
        self.repo = repo
        self.texts_dir = texts_dir
        self.project_root = project_root

        # State
        self.current_path = self.texts_dir

        layout = QVBoxLayout(self)

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
        
        path = item.data(PATH_ROLE)

        if not path:
            return  # Prevent None errors

        path = Path(path)
        logger.info("Item clicked in DocumentBrowserWidget: %r", path)

		# IF DIRECTORY
        if path.is_dir():
            self.current_path = path
            self.populate_file_list(self.current_path)
        # OTHERWISE IT IS FILE
        else:
            doc_id = self.repo.lookup_document_id(path)
            
            if doc_id is None:
                logger.warning("File not registered in documents: %r", path)
            else:
                logger.info("Clicked document: doc_id=%s path=%r", doc_id, path)
            
            self.document_activated.emit(path)
            
    def populate_file_list(self, directory: Path):
        """
        Populate the QListWidget with directories and files from the given directory.
        """
        directory = Path(directory)
        self.current_path = directory

        self.file_list.clear()

        # Enable or disable the back button based on directory
        # self.back_button.setEnabled(self.current_path != self.project_root)

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
            logger.error("Error accessing directory %r: %s", self.current_path,  e)

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
            self.memo_view_requested.emit(doc_id)
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
            self.document_renamed.emit(doc_id, new_name)

    def delete_document_from_ui(self, item, doc_id: int):
        rows, text_path = self.repo.delete_document(doc_id)
        logger.info("Repo deleted %s document(s) for id=%s, path=%r", rows, doc_id, text_path)

        if rows:
            # 1) Remove file from disk
            if text_path:
                try:
                    Path(text_path).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning("Failed to delete file %r: %s", text_path, e)

            # 2) Remove the item from the list
            row_index = self.file_list.row(item)
            self.file_list.takeItem(row_index)

            # Emit signal that document deleted
            self.document_deleted.emit(doc_id, text_path or "")

        else:
            logger.warning("No document deleted for id=%s", doc_id)