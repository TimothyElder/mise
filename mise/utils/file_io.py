import os
from docx import Document as DocxDocument
import markdown

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