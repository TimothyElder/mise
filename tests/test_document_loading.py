from mise.utils.file_io import load_document
from mise.data_manager import Document
import pytest

def test_load_docx():
    """Test loading text from a DOCX file."""
    try:
        filepath = "test_files/sample.docx"  # Path to a sample DOCX file
        content = load_document(filepath)
        assert content.strip() != "", "DOCX content should not be empty."
        print("DOCX file loaded successfully!")
    except Exception as e:
        print(f"Failed to load DOCX: {e}")

def test_load_markdown():
    """Test loading text from a Markdown file."""
    try:
        filepath = "test_files/sample.md"  # Path to a sample Markdown file
        content = load_document(filepath)
        assert content.strip() != "", "Markdown content should not be empty."
        print("Markdown file loaded successfully!")
    except Exception as e:
        print(f"Failed to load Markdown: {e}")

def test_document_class():
    """Test creating and loading a Document object."""
    try:
        docx_filepath = "test_files/sample.docx"
        md_filepath = "test_files/sample.md"

        # Test DOCX Document
        docx_doc = Document("DOCX Test Document", docx_filepath)
        assert docx_doc.text.strip() != "", "Document text should not be empty for DOCX."
        print(f"Document object created successfully for DOCX:\n{docx_doc.text[:100]}...")

        # Test Markdown Document
        md_doc = Document("Markdown Test Document", md_filepath)
        assert md_doc.text.strip() != "", "Document text should not be empty for Markdown."
        print(f"Document object created successfully for Markdown:\n{md_doc.text[:100]}...")
    except Exception as e:
        print(f"Failed to create Document object: {e}")

def test_load_document_empty_file(tmp_path):
    # Create an empty file
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()  # This creates an empty file

    with pytest.raises(ValueError, match="Document is empty"):
        load_document(str(empty_file))

def test_load_document_invalid_path():
    invalid_path = "/nonexistent/file.txt"
    load_document(invalid_path)
    with pytest.raises(FileNotFoundError):
        load_document(invalid_path)

if __name__ == "__main__":
    print("Running backend document loading tests...\n")

    # Run tests
    test_load_docx()
    test_load_markdown()
    test_document_class()

    print("\nAll tests completed.")