# src/mise/analysisview/document_stats_tree.py

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal

from ..utils.project_repository import ProjectRepository

# for cursor info
DOC_ID_ROLE = Qt.UserRole + 1
PATH_ROLE = Qt.UserRole + 2

class DocumentStatsTreeWidget(QTreeWidget):

    documentSelected = Signal(object, int)

    def __init__(self, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        self.repo = repo

        self.setColumnCount(4)
        self.setHeaderLabels([
            "Document Name",
            "Document ID",
            "Coded Segments",
            "Unique Codes",
        ])

        self.reload_data()

        self.itemClicked.connect(self.handle_item_click)

    def handle_item_click(self, item):
        path = item.data(0, PATH_ROLE)
        doc_id = item.data(0, DOC_ID_ROLE)
        if path is not None:
            self.documentSelected.emit(path, doc_id)
            

    def reload_data(self):
        self.clear()
        rows = self.repo.get_document_coding_overview()
        for row in rows:
            item = QTreeWidgetItem([
                str(row["display_name"]),
                str(row["doc_id"]),
                str(row["segment_count"]),
                str(row["unique_codes"]),
            ])
            item.setData(0, DOC_ID_ROLE, row["doc_id"])
            item.setData(0, PATH_ROLE, row["path"])
            self.addTopLevelItem(item)

    def current_document_id(self):
        item = self.currentItem()
        if not item:
            return None
        return item.data(0, Qt.UserRole)