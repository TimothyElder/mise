from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QDialogButtonBox, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt

class CodePickerDialog(QDialog):
    """
    Dialog for choosing an existing code to assign to a text selection.
    Reads codes from the `codes` table via the given DB connection.
    """
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self._selected_code_id = None

        self.setWindowTitle("Assign Code")

        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)  # just show labels
        layout.addWidget(self.tree)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.populate_codes()

    def list_codes(self):
        cur = self.conn.execute(
            "SELECT id, label, parent_id, color FROM codes ORDER BY label COLLATE NOCASE"
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def populate_codes(self):
        self.tree.clear()

        codes = self.list_codes()
        if not codes:
            return

        items_by_id = {}

        # Create items
        for code in codes:
            item = QTreeWidgetItem([code["label"]])
            item.setData(0, Qt.UserRole, code["id"])
            items_by_id[code["id"]] = item

        # Wire parent/child
        for code in codes:
            item = items_by_id[code["id"]]
            parent_id = code["parent_id"]
            if parent_id and parent_id in items_by_id:
                items_by_id[parent_id].addChild(item)
            else:
                self.tree.addTopLevelItem(item)

        self.tree.expandAll()

    def get_code_id(self):
        item = self.tree.currentItem()
        if not item:
            return None
        return item.data(0, Qt.UserRole)