import os
import csv
import json
from docx import Document as DocxDocument
import markdown
import pickle

from pathlib import Path
import pdfplumber

def convert_to_canonical_text(src_path: Path) -> str:
    ext = src_path.suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(src_path)
    elif ext == ".docx":
        return extract_text_from_docx(src_path)
    elif ext == ".doc":
        return extract_text_from_doc(src_path)
    elif ext in {".md", ".markdown"}:
        return extract_text_from_markdown(src_path)
    else:
        raise ValueError(f"Unsupported extension: {ext}")

def extract_text_from_pdf(path: Path) -> str:
    # Very basic implementation
    chunks = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            chunks.append(text)
    # Normalize to Unix line endings
    return "\n\n".join(chunks).replace("\r\n", "\n").replace("\r", "\n")

def extract_text_from_docx(path: Path) -> str:
    doc = DocxDocument(str(path))
    paragraphs = [p.text for p in doc.paragraphs]
    text = "\n\n".join(paragraphs)
    return text.replace("\r\n", "\n").replace("\r", "\n")

def extract_text_from_doc(path: Path) -> str:
    # Stub for now
    raise ValueError(".doc import is not yet implemented. Please convert to .docx or PDF first.")

def extract_text_from_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n")

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


