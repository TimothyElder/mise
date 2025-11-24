# Mise Code Style Guidelines

These conventions are **required** across all Python source files in the project.

---

## 1. Class Names
- **PascalCase**.
- Qt widgets **must end in `Widget`**.
- Container-level UI classes (things that assemble widgets) should end in **`View`**.

**Examples**
```python
class ProjectView(QWidget)
class DocumentBrowserWidget(QWidget)
class CodeTreeWidget(QTreeWidget)
class AnalysisView(QWidget)
```

---

## 2. Methods, Attributes, and Variables
- Use **snake_case**.
- Names must be **descriptive and unambiguous**.
- Avoid abbreviations unless they are domain-standard (e.g., `doc_id`, `path`, `repo`).

**Examples**
```python
def refresh_tree()
def load_document(path)
self.current_document_id
self.selected_code_label
```

---

## 3. Signals
- Named as **events**, not commands.
- Lowercase **snake_case**.
- Do not encode boolean meanings into names (e.g., avoid `*_updated(True)`).

**GOOD**
```
code_selected(code_id)
document_deleted(doc_id, path)
codes_updated()
```

**BAD**
```
on_code_clicked
codes_updated(True)
update_document_signal
```

---

## 4. Constants
- **ALL_CAPS**.
- Only for fixed configuration-type values.

**Examples**
```python
DOC_ID_ROLE = Qt.UserRole + 1
ASSETS_DIR = Path(__file__).parent / "assets"
DEFAULT_FONT_SIZE = 12
```

---

## 5. Repository / Database API
Methods that manipulate or fetch persistent data must:
- start with an **action verb**
- not contain any UI logic

**Required method prefixes**
```
add_x
update_x
delete_x
list_x
lookup_x
```

**Examples**
```python
add_code(label, parent_id)
update_code(code_id, label, color)
delete_code(code_id)
list_codes()
lookup_code(code_id)
```

---

## 6. File Names
- Must be **snake_case**.
- Should describe the file’s responsibility.

**Examples**
```
project_view.py
code_manager.py
document_browser_widget.py
analysis_view.py
```

---

## 9. Library imports

Library imports in each file should begin with general library imports such as `os`, `Path` or `logging`, then Pyside specific libraries, then Mise modules such as:

```py
import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .utils.logging_config import setup_logging

```

---
## 8. Conformance
Refactors for naming and consistency should be **separated from feature changes** to avoid mixed commits.

Commits or pull requests that introduce identifiers or patterns violating this document should be revised before merging. All new modules and features must follow this guide.
