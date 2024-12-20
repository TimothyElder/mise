import os

from mise.data_manager import Code, Document, Project
from mise.utils.gen_utils import is_pathname_valid

def create_project_directory(project_name: str, dirpath: str):
    if type(project_name) != str:
        raise TypeError("Project name must be string...")
    elif is_pathname_valid(dirpath) == False:
        raise ValueError("Error: specified path doesn't exist.")
    elif os.path.isdir(dirpath + "/" + project_name) == True:
        raise FileExistsError("Error: directory already exists.")
    else:
        os.mkdir(dirpath + "/" + project_name)
        os.mkdir(dirpath + "/" + project_name + "/" + "data")

def project_inventory(dirpath: str):
    os.listdir
