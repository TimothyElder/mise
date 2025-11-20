from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QDialog, QLineEdit, QComboBox, QLabel, QDialogButtonBox, QPlainTextEdit, QFormLayout
)
from PySide6.QtCore import Qt
import uuid

class AddCodeDialog(QDialog):
    """
    Simple dialog to add a new code.
    Lets you specify:
      - label (required)
      - parent (optional, chosen from existing codes)
      - description (optional)
    """
    def __init__(self, parent, codes):
        super().__init__(parent)
        self.setWindowTitle("Add Code")

        self.codes = codes  # list of sqlite Row objects

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.label_edit = QLineEdit()
        form.addRow("Label:", self.label_edit)

        self.parent_combo = QComboBox()
        # First option: no parent (top-level code)
        self.parent_combo.addItem("<No parent>", None)

        # Only allow *top-level* codes (parent_id is NULL) as parents
        for code in self.codes:
            if code["parent_id"] is None:
                self.parent_combo.addItem(code["label"], code["id"])
        
        form.addRow("Parent:", self.parent_combo)

        self.desc_edit = QPlainTextEdit()
        self.desc_edit.setPlaceholderText("Optional description...")
        form.addRow("Description:", self.desc_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        """
        Return dict with label, parent_id, description.
        """
        label = self.label_edit.text().strip()
        parent_id = self.parent_combo.currentData()
        description = self.desc_edit.toPlainText().strip()
        return {
            "label": label,
            "parent_id": parent_id,
            "description": description,
        }

class CodeManager(QWidget):
    def __init__(self, db_conn):
        super().__init__()
        self.conn = db_conn
        self.init_ui()
        self.refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Codes"])
        layout.addWidget(self.tree)

        add_button = QPushButton("Add Code")
        add_button.clicked.connect(self.add_code_dialog)
        layout.addWidget(add_button)

    # --- DB helpers ---

    def list_codes(self):
        """
        Return all codes as sqlite Row objects.
        Expected columns: id, label, parent_id, description, color, sort_order
        """
        return self.conn.execute(
            "SELECT id, label, parent_id, description, color, sort_order "
            "FROM codes "
            "ORDER BY sort_order, label"
        ).fetchall()

    def _next_sort_order(self):
        row = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), 0) AS max_so FROM codes"
        ).fetchone()
        return (row["max_so"] or 0) + 1

    def add_code(self, label, parent_id=None, description=""):
        """
        Insert a new code into the database with a generated id and sort_order.
        """
        code_id = str(uuid.uuid4())
        sort_order = self._next_sort_order()
        self.conn.execute(
            "INSERT INTO codes (id, label, parent_id, description, color, sort_order) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (code_id, label, parent_id, description, None, sort_order),
        )
        self.conn.commit()
        return code_id

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

        # Map id -> code row
        codes_by_id = {c["id"]: c for c in codes}

        # Map id -> QTreeWidgetItem
        items_by_id = {}

        # First create items for all codes
        for code in codes:
            item = QTreeWidgetItem([code["label"]])
            item.setData(0, Qt.UserRole, code["id"])
            items_by_id[code["id"]] = item

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
        dlg = AddCodeDialog(self, codes)
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
        )
        self.refresh()