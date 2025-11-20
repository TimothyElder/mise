
import os
from pathlib import Path
from .database import initialize_database
from .metadata import initialize_metadata
from mise.utils.gen_utils import is_pathname_valid


def create_project(project_name: str, dirpath: str) -> Path:
    """
    High-level project creation.
    Creates project directory, database, and metadata files.
    Returns project_root Path.
    """
   
    project_root = create_project_directory(project_name, dirpath)

    initialize_database(project_root)
    initialize_metadata(project_root)

    return project_root

def create_project_directory(project_name: str, dirpath: str) -> Path:
    dirpath = Path(dirpath)
    project_root = dirpath / f"{project_name}.mise"

    if not dirpath.exists():
        raise ValueError("Directory doesn't exist.")
    if project_root.exists():
        raise FileExistsError("Project already exists.")

    project_root.mkdir()
    (project_root / "texts").mkdir()
    (project_root / "meta").mkdir()

    return project_root