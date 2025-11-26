import os
import csv
import json
from docx import Document as DocxDocument
import markdown

from pathlib import Path
import pdfplumber

import logging
log = logging.getLogger(__name__)

def convert_to_canonical_text(src_path: Path) -> str:
    """
    Convert source document, uploaded by the user,
    to the canonical plaintext format. Returns plain text.
    """
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
    """
    Extract text from PDF document and return as plaintext.
    """
    chunks = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            chunks.append(text)

    log.info("extract_text_from_pdf: extracted content from %r", path)
    # Normalize to Unix line endings
    return "\n\n".join(chunks).replace("\r\n", "\n").replace("\r", "\n")

def extract_text_from_docx(path: Path) -> str:
    """
    Extract text from Docx document and return as plaintext.
    """
    doc = DocxDocument(str(path))
    paragraphs = [p.text for p in doc.paragraphs]
    text = "\n\n".join(paragraphs)
    log.info("extract_text_from_docx: extracted content from %r", path)
    return text.replace("\r\n", "\n").replace("\r", "\n")

def extract_text_from_doc(path: Path) -> str:
    # Stub for now
    raise ValueError(".doc import is not yet implemented. Please convert to .docx or PDF first.")

def extract_text_from_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    log.info("extract_text_from_markdown: extracted content from %r", path)
    return text.replace("\r\n", "\n").replace("\r", "\n")