# src/mise/analysisview/code_viewer.py

import logging
logger = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal, QSize

from ..utils.project_repository import ProjectRepository

# custom roles
DOC_ID_ROLE = Qt.UserRole + 1
START_ROLE = Qt.UserRole + 2
END_ROLE = Qt.UserRole + 3

class SegmentCardWidget(QWidget):
    """
    Visual card for a single coded segment:
      - Document name (bold)
      - Offsets (small, muted)
      - Snippet (wrapped)
    """

    def __init__(self, document_name: str, start: int, end: int, snippet: str, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(3)

        # Top row: document name + offsets
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        doc_label = QLabel(document_name)
        font = doc_label.font()
        font.setBold(True)
        doc_label.setFont(font)

        offsets_label = QLabel(f"{start} – {end}")
        offsets_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        offsets_label.setStyleSheet("color: #666666; font-size: 11px;")

        top_row.addWidget(doc_label, 1)
        top_row.addWidget(offsets_label, 0)

        # Snippet: wrapped text
        snippet_label = QLabel(snippet)
        snippet_label.setWordWrap(True)
        snippet_label.setStyleSheet("font-size: 12px;")

        layout.addLayout(top_row)
        layout.addWidget(snippet_label)

    def sizeHint(self) -> QSize:
        base = super().sizeHint()
        return QSize(base.width(), max(base.height(), 60))


class CodeSegmentView(QWidget):
    """
    Right-hand panel in AnalysisView when a code is selected.
    Shows all segments coded with that code across documents as cards.
    """

    segmentActivated = Signal(int, int, int)
    # document_id, start_offset, end_offset, text_path

    def __init__(self, repo: ProjectRepository, parent=None):
        super().__init__(parent)
        self.repo = repo

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setUniformItemSizes(False)  # allow variable-height cards
        self.list.setSpacing(4)

        layout.addWidget(self.list)

        self.list.itemDoubleClicked.connect(self._on_item_activated)

    def clear(self):
        self.list.clear()

    def get_text_snippet(self, text_path: str, start_offset: int, end_offset: int) -> str:
        # text_path is the DB path (now relative); resolve it against the repo's texts_dir
        abs_path = (self.repo.texts_dir / text_path).resolve()

        content = abs_path.read_text(encoding="utf-8")
        snippet = content[start_offset:end_offset]
        return snippet.strip()

    def load_segments_for_code(self, code_id: int):
        """
        Populate the list with all segments coded with this code.
        Expects repo.get_segments_for_code(code_id) to return rows with:
          - document_id
          - display_name
          - text_path
          - start_offset
          - end_offset
        """
        self.list.clear()

        rows = self.repo.get_segments_for_code(code_id)
        logger.debug("CodeSegmentView: loaded %d segments for code_id=%s", len(rows), code_id)

        for seg in rows:
            doc_label = seg["display_name"]
            text_path = seg["text_path"]
            start = seg["start_offset"]
            end = seg["end_offset"]
            snippet = self.get_text_snippet(text_path=text_path, start_offset=start, end_offset=end)

            item = QListWidgetItem()
            card = SegmentCardWidget(doc_label, start, end, snippet, parent=self.list)

            # store metadata
            item.setData(DOC_ID_ROLE, seg["document_id"])
            item.setData(START_ROLE, start)
            item.setData(END_ROLE, end)

            item.setSizeHint(card.sizeHint())

            self.list.addItem(item)
            self.list.setItemWidget(item, card)

    def _on_item_activated(self, item: QListWidgetItem):
        doc_id = item.data(DOC_ID_ROLE)
        start = item.data(START_ROLE)
        end = item.data(END_ROLE)

        if doc_id is None or start is None or end is None:
            return

        self.segmentActivated.emit(doc_id, start, end)