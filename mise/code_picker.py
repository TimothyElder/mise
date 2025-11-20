from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDialogButtonBox, QLabel
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

        self.setWindowTitle("Assign Code")
        self._init_ui()
        self._load_codes()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel("Choose a code to assign to the selected text:")
        layout.addWidget(info)

        form = QFormLayout()
        self.code_combo = QComboBox()
        form.addRow("Code:", self.code_combo)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal,
            parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_codes(self):
        self.code_combo.clear()

        rows = self.conn.execute(
            "SELECT id, label, parent_id FROM codes ORDER BY sort_order, label"
        ).fetchall()

        for row in rows:
            label = row["label"]
            if row["parent_id"] is not None:
                display_text = f"  {label}"
            else:
                display_text = label

            self.code_combo.addItem(display_text, row["id"])

        if self.code_combo.count() == 0:
            self.code_combo.addItem("(No codes defined)", None)

    def get_code_id(self):
        """
        Return the selected code's ID (from codes.id), or None.
        Call this only after exec() returns QDialog.Accepted.
        """
        return self.code_combo.currentData()