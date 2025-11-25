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
from datetime import datetime
from html import escape
import webbrowser

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
    
    # ---------- reports ------------------------------

    def generate_report(self, report_data: list[dict]):
            """
            report_data = [
                {
                    "code": {
                        "id": int,
                        "label": str,
                        "color": str,
                        "segment_count": int,
                        "document_count": int,
                    },
                    "segments": [
                        {
                            "document_id": int,
                            "display_name": str,
                            "text_path": str,
                            "start_offset": int,
                            "end_offset": int
                        },
                        ...
                    ]
                },
                ...
            ]
            """

            if not report_data:
                log.warning("generate_report called with empty report_data.")
                return

            # --------------------------------------------
            # 1. Load HTML template
            # --------------------------------------------
            template_path = (
                Path(__file__).resolve().parent
                / "assets"
                / "templates"
                / "template.html"
            )

            try:
                template = template_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                log.error("Template not found at %r", template_path)
                return

            # --------------------------------------------
            # 2. Generate report body (inner HTML)
            # --------------------------------------------
            project_name = escape(getattr(self, "current_project_name", "Unknown Project"))
            body_parts = []

            for entry in report_data:
                code = entry["code"]
                segments = entry["segments"]

                code_label = escape(code["label"])
                code_color = escape(code.get("color") or "#cccccc")
                segment_count = code.get("segment_count", len(segments))
                document_count = code.get("document_count", None)

                # ----- Code header block -----
                body_parts.append(
                    f"<section>\n"
                    f"<h2><span class='code-badge' "
                    f"style='border-color:{code_color};background:{code_color}22;'>"
                    f"{code_label}</span></h2>\n"
                    f"<p>Project: {project_name}</p>\n"
                    f"<p>Segments: {segment_count}"
                    + (f" | Documents: {document_count}</p>\n" if document_count else "</p>\n")
                )

                # ----- Group segments by document -----
                docs = {}
                for seg in segments:
                    doc = seg["display_name"]
                    docs.setdefault(doc, []).append(seg)

                # ----- Write segments for each document -----
                for doc_name, seg_list in docs.items():
                    body_parts.append(f"<h3>{escape(doc_name)}</h3>\n")

                    for seg in seg_list:
                        path = seg["text_path"]
                        start = seg["start_offset"]
                        end = seg["end_offset"]

                        try:
                            content = Path(path).read_text(encoding="utf-8")
                            snippet = escape(content[start:end].strip())
                        except Exception as e:
                            snippet = "[Error reading snippet]"
                            log.warning(f"Error reading snippet for {path}: {e}")

                        body_parts.append(
                            "<div class='segment'>\n"
                            f"  <div class='segment-header'>Offsets: {start}–{end} | Path: {escape(path)}</div>\n"
                            f"  <div class='snippet'>{snippet}</div>\n"
                            "</div>\n"
                        )

                body_parts.append("</section>\n")

            body_html = "".join(body_parts)
            
            # --------------------------------------------
            # 2b. Fill PROJECT_NAME
            # --------------------------------------------
            project_name = getattr(self, "current_project_name", "Unknown Project")
            template = template.replace("{{PROJECT_NAME}}", escape(project_name))

            logo_path = (
                Path(__file__).resolve().parent / "assets" / "mise.png"
            ).as_uri()

            template = template.replace("{{LOGO_PATH}}", logo_path)

            # --------------------------------------------
            # 3. Fill template (replace {{CONTENT}})
            # --------------------------------------------
            if "{{CONTENT}}" in template:
                full_html = template.replace("{{CONTENT}}", body_html)
            else:
                # fallback: append at end
                full_html = template + "\n" + body_html

            # --------------------------------------------
            # 4. Save report to project_root/reports/
            # --------------------------------------------
            reports_dir = self.current_project_root / "reports"
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name = f"code-report-{timestamp}.html"

            out_path = reports_dir / file_name
            out_path.write_text(full_html, encoding="utf-8")

            try:
                webbrowser.open(out_path.as_uri())
            except Exception as e:
                log.warning("Could not open report automatically: %s", e)

            log.info("Report successfully written to %r", out_path)

    # ---------- shutdown ------------------------------

    def shutdown(self):
        # Single place to close the repo
        if self.current_repo is not None:
            self.current_repo.close()