from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QColorDialog,
    QDialog, QLineEdit, QComboBox, QDialogButtonBox, QPlainTextEdit, QFormLayout,
    QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from ..utils.project_repository import ProjectRepository

class CodeManager(QWidget):
    codes_updated = Signal(bool) 

    def __init__(self, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.init_ui()
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.tree = CodeTreeWidget()
        self.tree.setHeaderLabels(["Code", "Color"])
        self.tree.setColumnCount(2)
        self.tree.setColumnWidth(1, 40)  # narrow color column
        layout.addWidget(self.tree)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)

        add_button = QPushButton("Add Code")
        add_button.clicked.connect(self.add_code_dialog)
        layout.addWidget(add_button)

    # --- DB helpers ---
    def edit_code(self, code_id, label=None, parent_id=None, description=None, color=None):
        """
        Edit extant code attributes.
        """
        updated = self.repo.update_code(
            code_id=code_id,
            label=label,
            parent_id=parent_id,
            description=description,
            color=color,
        )

        if updated == 0:
            raise ValueError(f"No code found with id={code_id}")
        
        if updated > 0:
            self.codes_updated.emit(True)
            print("SIGNAL EMITED")

        return updated

    def list_codes(self):
        """
        Return all codes as sqlite Row objects.
        """
        return self.repo.list_codes()

    def add_code(self, label, parent_id=None, description="", color=""):
        """
        Insert a new code into the database.
        """
        return self.repo.add_code(label=label, parent_id=parent_id, description=description, color=color)

    # --- Tree population ---
    def refresh(self):
        """
        Refresh the tree widget from DB contents.
        Builds a parent/child hierarchy based on parent_id.
        """
        self.tree.clear()

        codes = self.list_codes()
        if not codes:
            return

        # Map id -> QTreeWidgetItem
        items_by_id = {}

        # First create items for all codes
        for code in codes:
            # two columns: label, color swatch
            item = QTreeWidgetItem([code["label"], ""])
            item.setData(0, Qt.UserRole, code["id"])
            items_by_id[code["id"]] = item

            color = code["color"]
            if color:
                qcolor = QColor(color)
                if qcolor.isValid():
                    # only color the second column’s background
                    item.setBackground(1, qcolor)

        # Attach them according to parent_id
        for code in codes:
            item = items_by_id[code["id"]]
            parent_id = code["parent_id"]

            if parent_id and parent_id in items_by_id:
                # Add as child of its parent
                items_by_id[parent_id].addChild(item)
            else:
                # No parent: top-level code
                self.tree.addTopLevelItem(item)

        self.tree.expandAll()

    # --- UI actions ---
    def add_code_dialog(self):
        """
        Show the Add Code dialog, and if accepted, insert code and refresh tree.
        """
        codes = self.list_codes()
        dlg = CodeDialog(self, codes)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        if not data["label"]:
            # Minimal guard; you can add a message box if you care
            return

        self.add_code(
            label=data["label"],
            parent_id=data["parent_id"],
            description=data["description"],
            color=data["color"],
        )

        self.refresh()

    def open_context_menu(self, pos):
        """
        Context menu for the code tree.
        """

        menu = QMenu(self)

        item = self.tree.itemAt(pos)
        if item is None:
            return  # right-click on empty area

        code_id = item.data(0, Qt.UserRole)  # or wherever you stored it

        edit = menu.addAction("Edit Code…")
        edit.triggered.connect(lambda: self._on_edit_code_requested(code_id))

        delete = menu.addAction("Delete Code…")
        delete.triggered.connect(lambda: self._on_delete_code_requested(code_id))

        global_pos = self.tree.viewport().mapToGlobal(pos)
        menu.exec(global_pos)

    def _on_delete_code_requested(self, code_id):
        """
        Send delete request to ProjectRepository
        """
        self.repo.delete_code(code_id)
        print(f"deleted code ID == {code_id}")

        self.refresh()
        self.codes_updated.emit()
    
    def _on_edit_code_requested(self, code_id):

        # fetch current code info
        row = self.repo.lookup_code(code_id)

        # get user input
        codes = self.list_codes()
        dlg = CodeDialog(parent=self, codes=codes, existing=row)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        # data returns 
        # {'label': 'pain-service', 'parent_id': None, 'description': 'A pain service one', 'color': '#ff6a88'}

        # send user input to databas
        self.edit_code(
            code_id=code_id,
            label=data["label"],
            parent_id=data["parent_id"],
            description=data["description"],
            color=data["color"],
        )

        self.refresh()

class CodeDialog(QDialog):
    """
    Simple dialog to add a new code and edit codes.
    Lets you specify:
      - label (required)
      - parent (optional, chosen from existing codes)
      - description (optional)
    """
    def __init__(self, parent, codes, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Code" if existing else "Add Code")

        self.codes = codes
        self.color = None

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.label_edit = QLineEdit()
        form.addRow("Label:", self.label_edit)

        self.parent_combo = QComboBox()
        # no parent (top-level code)
        self.parent_combo.addItem("<No parent>", None)

        # Only allow *top-level* codes (parent_id is NULL) as parents
        for code in self.codes:
            if code["parent_id"] is None:
                self.parent_combo.addItem(code["label"], code["id"])
        
        form.addRow("Parent:", self.parent_combo)

        self.desc_edit = QPlainTextEdit()
        self.desc_edit.setPlaceholderText("Optional description...")
        form.addRow("Description:", self.desc_edit)

        # Color picker button
        self.color_button = QPushButton("Choose color…")
        self.color_button.clicked.connect(self._pick_color)
        form.addRow("Color:", self.color_button)

        layout.addLayout(form)

        if existing is not None:
            self.label_edit.setText(existing["label"])
            self.desc_edit.setPlainText(existing["description"] or "")
            self.color = QColor(existing["color"]) if existing["color"] else None
            if self.color:
                self.color_button.setText(self.color.name())

            # parent
            index = self.parent_combo.findData(existing["parent_id"])
            if index >= 0:
                self.parent_combo.setCurrentIndex(index)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal,
            parent=self
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _pick_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.color = color
            self.color_button.setText(color.name())
            

    def get_data(self):
        label = self.label_edit.text().strip()      # must be non-empty; enforce in dialog
        parent_id = self.parent_combo.currentData() # None for <No parent>, fine
        description = self.desc_edit.toPlainText().strip()
        color = self.color.name() if self.color else None

        return {
            "label": label,
            "parent_id": parent_id,
            "description": description,
            "color": color,
        }

class CodeTreeWidget(QTreeWidget):
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            self.clearSelection()
        super().mousePressEvent(event)