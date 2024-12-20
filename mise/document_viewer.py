from PySide6.QtWidgets import QMainWindow, QTextBrowser, QVBoxLayout, QWidget
from mise.utils.file_io import load_document

class DocumentViewer(QMainWindow):
    def __init__(self, filepath):
        super().__init__()
        self.setWindowTitle("Document Viewer")
        self.resize(800, 600)

        # Load the document
        content = load_document(filepath)

        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Display content
        self.text_browser = QTextBrowser()
        if filepath.endswith(".md"):
            from markdown import markdown
            self.text_browser.setHtml(markdown(content))  # Render Markdown as HTML
        else:
            self.text_browser.setPlainText(content)  # Show plain text for DOCX
        
        layout.addWidget(self.text_browser)