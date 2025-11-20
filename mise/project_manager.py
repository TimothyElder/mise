import os

from mise.data_manager import Code, Document, Project
from mise.utils.gen_utils import is_pathname_valid
from mise.utils.file_io import convert_to_canonical_text

def create_project_directory(project_name: str, dirpath: str):
    
    project_directory_name = project_name + ".mise"

    project_root = os.path.join(dirpath, project_directory_name)
    
    if is_pathname_valid(dirpath) == False:
        raise ValueError("Error: specified path doesn't exist.")
    elif os.path.isdir(project_root) == True:
        raise FileExistsError("Error: directory already exists.")
    else:
        os.mkdir(project_root)
        os.mkdir(os.path.join(dirpath, project_directory_name, "texts"))
        os.mkdir(os.path.join(dirpath, project_directory_name, "meta"))

    return project_root

def project_inventory(dirpath: str):
    os.listdir
