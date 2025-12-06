from pathlib import Path
from .database import initialize_database
from .metadata import initialize_metadata

import logging
logger = logging.getLogger(__name__)

def init_project(project_name: str, dirpath: str) -> Path:
    """
    High-level project creation.
    Calls function that creates directory and touches off database
    and metadata
    Returns project_root Path.
    """
   
    project_root = create_project_directory(project_name, dirpath)

    initialize_database(project_root)
    initialize_metadata(project_root)

    return project_root

def create_project_directory(project_name: str, dirpath: str) -> Path:
    """
    Creates the directory for the project with subdirectories for metadata
    and text data
    Returns project_root path
    """

    dirpath = Path(dirpath)
    project_root = dirpath / f"{project_name}.mise"

    if not dirpath.exists():
        logger.error("Directory doesn't exist on create project at %r", project_root)
        raise ValueError("Directory doesn't exist.")
        
    if project_root.exists():
        logger.error("Directory already exist on create project at %r", project_root)
        raise FileExistsError("Project already exists.")

    project_root.mkdir()
    (project_root / "texts").mkdir()
    (project_root / "meta").mkdir()

    return project_root