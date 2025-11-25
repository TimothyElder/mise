# src/mise/analysisview/code_stats_tree.py

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from ..utils.project_repository import ProjectRepository

class CodeStatsTreeWidget(QTreeWidget):

    codeSelected = Signal(object)

    def __init__(self, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        self.repo = repo

        self.setColumnCount(4)
        self.setHeaderLabels([
            "Code Name",
            "Color",
            "Times Used",
            "Documents Used In",
        ])

        self.reload_data()

    def reload_data(self):
        self.clear()
        rows = self.repo.get_code_usage_overview()

        for row in rows:
            color_hex = row["color"] or ""

            item = QTreeWidgetItem([
                row["label"],
                "",   # <-- leave color column text empty
                str(row["segment_count"]),
                str(row["document_count"]),
            ])

            # Store code ID (you probably want ID, not label)
            item.setData(0, Qt.UserRole, row["id"])
            self.itemClicked.connect(self.handle_code_click)

            # Apply background color to the Color column (col 1)
            if color_hex:
                color = QColor(color_hex)
                brush = QBrush(color)
                item.setBackground(1, brush)

                # Tooltip with the hex code
                item.setToolTip(1, color_hex)

            self.addTopLevelItem(item)

    def current_code_id(self):
        item = self.currentItem()
        if not item:
            return None
        return item.data(0, Qt.UserRole)
    
    def handle_code_click(self, item):
        code_id = item.data(0, Qt.UserRole)
        if code_id is not None:
            self.codeSelected.emit(code_id)
        