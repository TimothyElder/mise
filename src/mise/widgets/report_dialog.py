# src/mise/analysisview/code_report_dialog.py

import logging
logger = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt

from ..utils.project_repository import ProjectRepository

CODE_ID_ROLE = Qt.UserRole + 1


class CodeReportDialog(QDialog):
    """
    Dialog to select which codes to include in a report.
    Uses get_code_usage_overview() from ProjectRepository.
    """

    def __init__(self, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        self.repo = repo

        self.setWindowTitle("Generate Code Reports")

        layout = QVBoxLayout(self)

        # Code list
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels([
            "Code",
            "Color",
            "Segments",
            "Documents",
        ])
        layout.addWidget(self.tree)

        self._populate_codes()

        # Buttons: OK / Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_codes(self):
        self.tree.clear()
        rows = self.repo.get_code_usage_overview()
        # rows: [{id, label, color, segment_count, document_count}, ...]

        for row in rows:
            item = QTreeWidgetItem([
                row["label"],
                row["color"] or "",
                str(row["segment_count"]),
                str(row["document_count"]),
            ])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            item.setData(0, CODE_ID_ROLE, row["id"])
            self.tree.addTopLevelItem(item)

    def get_selected_code_ids(self):
        """
        Call this after exec_() == QDialog.Accepted.
        Returns a list of code_ids that were checked.
        """
        selected = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                code_id = item.data(0, CODE_ID_ROLE)
                if code_id is not None:
                    selected.append(code_id)
        return selected