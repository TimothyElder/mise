import logging
log = logging.getLogger(__name__)

from pathlib import Path


from PySide6.QtGui import QTextOption, QFontMetrics
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QStyledItemDelegate
from PySide6.QtCore import Qt, Signal, QSize

from ..utils.project_repository import ProjectRepository

# custom roles
DOC_ID_ROLE = Qt.UserRole + 1
START_ROLE = Qt.UserRole + 2
END_ROLE = Qt.UserRole + 3
PATH_ROLE = Qt.UserRole + 4   # optional, if your query returns it


class CodeSegmentView(QWidget):
    """
    Right-hand panel in AnalysisView when a code is selected.
    Shows all segments coded with that code across documents.
    """

    segmentActivated = Signal(int, int, int, object)  
    # document_id, start_offset, end_offset, text_path (optional)

    def __init__(self, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        self.repo = repo

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels([
            "Document",
            "Start",
            "End",
            "Snippet",
        ])

        layout.addWidget(self.tree)

        # react to double-click or click as you prefer
        self.tree.itemDoubleClicked.connect(self._on_item_activated)

    def clear(self):
        self.tree.clear()

    def get_text_snippet(self, text_path: str, start_offset: int, end_offset: int):
        content = Path(text_path).read_text()
        snippet = content[start_offset:end_offset]

        return(snippet)

    def load_segments_for_code(self, code_id: int):
        """
        Populate the tree with all segments coded with this code.
        You need a repo method that returns rows with at least:
          - document_id
          - document_label or name
          - start_offset
          - end_offset
          - snippet (text)
          - optionally text_path
        """
        self.tree.clear()

        rows = self.repo.get_segments_for_code(code_id)

        log.debug("CodeSegmentView: loaded %d segments for code_id=%s", len(rows), code_id)

        for seg in rows:
            doc_label = seg["display_name"]
            text_path = seg["text_path"]
            start = seg["start_offset"]
            end = seg["end_offset"]
            snippet = self.get_text_snippet(text_path=text_path, start_offset = start, end_offset = end)

            item = QTreeWidgetItem([
                doc_label,
                str(start),
                str(end),
                snippet,
            ])

            item.setData(0, DOC_ID_ROLE, seg["document_id"])
            item.setData(0, START_ROLE, start)
            item.setData(0, END_ROLE, end)
            item.setData(0, PATH_ROLE, seg.get("text_path"))  # if available

            self.tree.addTopLevelItem(item)

        self.tree.resizeColumnToContents(0)  # document
        self.tree.resizeColumnToContents(1)  # start
        self.tree.resizeColumnToContents(2)  # end

    def _on_item_activated(self, item, column):
        doc_id = item.data(0, DOC_ID_ROLE)
        start = item.data(0, START_ROLE)
        end = item.data(0, END_ROLE)
        path = item.data(0, PATH_ROLE)

        if doc_id is None or start is None or end is None:
            return

        self.segmentActivated.emit(doc_id, start, end, path)