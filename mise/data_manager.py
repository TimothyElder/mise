import json
from mise.utils.file_io import load_document
from mise.utils.text_processing import documentTokenizer
from mise.code_manager import CodeManager

class Code:
    """
    The Code class defines the basic atom of Mise, the codes and their related
    descriptions that are ultimately applied to documents. 
    """
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def to_dict(self):
        return {"name": self.name, "description": self.description}

class Document:
    """
    Documents are the unit to which codes are applied. 
    """
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        self.text = self.load_text()

        try: 
            self.token_df = documentTokenizer(self.text, granularity="sentence")
        except Exception as e:
            raise ValueError(f"Failed to tokenize document '{self.name}': {e}")

    def load_text(self):
        return load_document(self.filepath)
    
    def assign_code_to_segment(self, code_name: str, segment_index: int, code_manager: CodeManager) -> None:
        if code_name not in code_manager.codes:
            raise ValueError(f"Code '{code_name}' does not exist.")
        if segment_index < 0 or segment_index >= len(self.token_df):
            raise IndexError("Invalid segment index.")
        self.token_df.loc[segment_index, "Codes"].append(code_name)

class Project:
    """
    The Project class gathers Codes and Documents together to be stored in a structured way.
    """

    def __init__(self, name):
        self.name = name
        self.documents = []

    def add_document(self, document):
        if not isinstance(document, Document):
            raise TypeError("Only objects of class 'Document' can be added.")
        
        self.documents.append(document)

    def save_project(self, filepath):
        data = {
            "name": self.name,
            "documents": [doc.to_dict() for doc in self.documents],
        }
        with open(filepath, "w") as f:
            json.dump(data, f)

    def load_project(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.name = data["name"]
        self.documents = [Document(**doc) for doc in data["documents"]]