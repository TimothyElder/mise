"""
Single source of truth for project state and views.

At minimum, AppController should own:
	•	Current project context
	•	current_project_name: str | None
	•	current_project_root: Path | None
	•	current_repo: ProjectRepository | None
	•	The “main” views for that project
	•	_project_view: ProjectView | None
	•	_analysis_view: AnalysisView | None

And high-level operations:
	•	create_project(name: str, base_dir: Path)
	•	open_project(project_root: Path)
	•	show_project_view()
	•	show_analysis_view()
"""

from pathlib import Path
import logging
log = logging.getLogger(__name__)
from typing import Optional

from PySide6.QtWidgets import QMainWindow, QMessageBox

from .utils.project_repository import ProjectRepository
from .projectview.project_window import ProjectView
from .analysisview.analysis_window import AnalysisView
from .project_init import create_project

class AppController:
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
    
    # ---------- state changes ----------
        self.current_project_name: Optional[str] = None
        self.current_project_root: Optional[Path] = None
        self.current_repo: Optional[ProjectRepository] = None

        self._project_view: Optional[ProjectView] = None
        self._analysis_view: Optional[AnalysisView] = None

    # ---------- project lifecycle ----------

    def create_project(self, project_name: str, base_dir: Path):
        project_root = create_project(project_name, str(base_dir))
        db_path = project_root / "project.db"
        repo = ProjectRepository(db_path)
        self._set_current_project(project_name, project_root, repo)
        self._create_project_view_if_needed()
        self.show_project_view()
        log.info("Project %s created at %r.", project_name, project_root)

    def open_project(self, project_root: Path):
        if not project_root.is_dir():
            QMessageBox.warning(self.main_window, "Invalid project", "The selected path is not a directory.")
            return

        if not (project_root / ".mise").exists():
            QMessageBox.warning(
                self.main_window,
                "Invalid project",
                "The selected folder does not appear to be a Mise project.\n"
            )
            return

        project_name = project_root.name
        if project_name.endswith(".mise"):
            project_name = project_name[:-5]

        db_path = project_root / "project.db"
        repo = ProjectRepository(db_path)

        self._set_current_project(project_name, project_root, repo)
        self._create_project_view_if_needed()
        self.show_project_view()

    def _set_current_project(self, name: str, root: Path, repo: ProjectRepository):
        self.current_project_name = name
        self.current_project_root = root
        self.current_repo = repo

        # Any existing views are now tied to a stale project → drop them
        self._project_view = None
        self._analysis_view = None

    # ---------- view management ----------

    def _create_project_view_if_needed(self):
        if self.current_repo is None:
            return
        if self._project_view is None:
            self._project_view = ProjectView(
                self.current_project_name,
                self.current_project_root,
                self.current_repo,
            )

    def _create_analysis_view_if_needed(self):
        if self.current_repo is None:
            QMessageBox.warning(
                self.main_window,
                "No project open",
                "Open or create a project before using the analysis view.",
            )
            return
        if self._analysis_view is None:
            self._analysis_view = AnalysisView(
                self.current_project_name,
                self.current_project_root,
                self.current_repo,
            )

    def show_project_view(self):
        if self.current_repo is None:
            QMessageBox.warning(self.main_window, "No project", "Open or create a project first.")
            return

        view = ProjectView(
            self.current_project_name,
            self.current_project_root,
            self.current_repo,
        )
        self._project_view = view
        self.main_window.setCentralWidget(view)

    def show_analysis_view(self):
        if self.current_repo is None:
            QMessageBox.warning(self.main_window, "No project", "Open or create a project first.")
            return

        view = AnalysisView(
            self.current_project_name,
            self.current_project_root,
            self.current_repo,
        )
        self._analysis_view = view
        self.main_window.setCentralWidget(view)

    # ---------- shutdown ----------

    def shutdown(self):
        # Single place to close the repo
        if self.current_repo is not None:
            self.current_repo.close()