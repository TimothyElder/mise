import json
from mise.utils.file_io import load_document

class Code:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def to_dict(self):
        return {"name": self.name, "description": self.description}

class Document:
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        self.text = self.load_text()

    def load_text(self):
        return load_document(self.filepath)

class Project:
    def __init__(self, name):
        self.name = name
        self.documents = []

    def add_document(self, document):
        self.documents.append(document)

    def save(self, filepath):
        data = {
            "name": self.name,
            "documents": [doc.to_dict() for doc in self.documents],
        }
        with open(filepath, "w") as f:
            json.dump(data, f)

    def load(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.name = data["name"]
        self.documents = [Document(**doc) for doc in data["documents"]]