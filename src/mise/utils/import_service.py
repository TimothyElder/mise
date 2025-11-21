from pathlib import Path
from .file_io import convert_to_canonical_text

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".md", ".markdown"}

def import_files(src_paths: list[Path], texts_dir: Path, repo) -> tuple[bool, list[str]]:
    imported_any = False
    errors = []

    for src_path in src_paths:
        ext = src_path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"{src_path.name}: unsupported extension '{ext}'")
            continue

        try:
            text = convert_to_canonical_text(src_path)
            dest_path = allocate_text_path(texts_dir)
            dest_path.write_text(text, encoding="utf-8")
            repo.register_document(src_path.name, dest_path)
            imported_any = True
        except Exception as e:
            errors.append(f"{src_path.name}: {e}")

    return imported_any, errors

def allocate_text_path(texts_dir: Path) -> Path:
    existing = list(texts_dir.glob("doc-*.txt"))
    next_id = len(existing) + 1
    return texts_dir / f"doc-{next_id:04d}.txt"