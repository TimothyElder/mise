import tempfile
from pathlib import Path
from mise.repository import ProjectRepository  # or whatever your module is

def test_create_and_reopen_project(tmp_path):
    project_dir = tmp_path / "my_project"
    repo = ProjectRepository.create(project_dir)

    # basic invariant: DB is initialized and readable
    assert project_dir.exists()
    assert (project_dir / "project.db").exists()

    # reopen
    repo2 = ProjectRepository.open(project_dir)
    assert repo2.list_documents() == []