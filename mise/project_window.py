from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QTextBrowser, QLabel

class ProjectWindow(QMainWindow):
    def __init__(self, project_name, project_path):
        super().__init__()
        self.setWindowTitle(f"Mise - {project_name}")
        self.resize(1200, 800)

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QHBoxLayout(central_widget)

        # Left: File list
        self.file_list = QListWidget()
        self.file_list.addItem("Example Document 1")  # Placeholder
        self.file_list.addItem("Example Document 2")  # Placeholder
        main_layout.addWidget(self.file_list)

        # Center: Document Viewer
        self.document_viewer = QTextBrowser()
        self.document_viewer.setText("Select a document to view its content.")  # Placeholder
        main_layout.addWidget(self.document_viewer)

        # Right: Code Manager
        self.code_manager = QLabel("Code Manager Placeholder")  # Replace with a real widget later
        main_layout.addWidget(self.code_manager)


    #     Next Steps
	# 1.	Populate the File List:
	# •	Dynamically load files from the project directory.
	# 2.	Implement Document Viewer:
	# •	Integrate your existing DocumentViewer class into the center panel.
	# 3.	Implement Code Manager:
	# •	Add functionality to manage codes on the right panel.