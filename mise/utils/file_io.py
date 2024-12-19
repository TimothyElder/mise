import os
import csv
import json
from docx import Document as DocxDocument
import markdown
import pickle

def read_docx(filepath):
    """Reads a DOCX file and returns its text content."""
    doc = DocxDocument(filepath)
    return "\n".join([p.text for p in doc.paragraphs])

def read_markdown(filepath):
    """Reads a Markdown file and returns its plain text content."""
    with open(filepath, "r") as f:
        return f.read()

def load_document(filepath):
    """Detects file type and loads the document."""
    _, ext = os.path.splitext(filepath)
    if ext.lower() == ".docx":
        return read_docx(filepath)
    elif ext.lower() in [".md", ".markdown"]:
        return read_markdown(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
def save_codes_to_csv(dictionary, filepath):
     """Saves code dictionary to csv"""
     with open(filepath, 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in dictionary.items():
            writer.writerow([key, value])

def save_codes_to_pickle(dictionary, filepath):
    """Saves code dictionary to pickle format"""
    with open(filepath, 'wb') as f:
        pickle.dump(dictionary, f)


def save_codes_to_json(dictionary, filepath):
    """Saves code dictionary to json"""
    with open(filepath, 'w') as f:
        json.dump(dictionary, f)

def load_codes_from_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def load_codes_from_csv(filepath):
    _, ext = os.path.splitext(filepath)
    if ext.lower() != ".csv":
        raise ValueError("file is not a .csv file type")
    else:
        with open(f'{filepath}') as csv_file:
            reader = csv.reader(csv_file)
            dictionary = dict(reader)
    
    return(dictionary)