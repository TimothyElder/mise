import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QListWidget, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the main window properties
        self.setWindowTitle("QDA Tool")
        self.setGeometry(100, 100, 800, 600)

        # Initialize the main layout
        self.init_ui()

    def init_ui(self):
        # Create main layout
        layout = QHBoxLayout()

        # Left panel (Text area for documents)
        left_panel = QVBoxLayout()
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Load and display text here...")
        left_panel.addWidget(self.text_area)

        # Add file load button
        load_file_button = QPushButton("Load File")
        load_file_button.clicked.connect(self.load_file)
        left_panel.addWidget(load_file_button)

        # Right panel (Code management)
        right_panel = QVBoxLayout()
        self.code_list = QListWidget()
        right_panel.addWidget(self.code_list)

        # Add buttons for code management
        add_code_button = QPushButton("Add Code")
        add_code_button.clicked.connect(self.add_code)
        right_panel.addWidget(add_code_button)

        delete_code_button = QPushButton("Delete Code")
        delete_code_button.clicked.connect(self.delete_code)
        right_panel.addWidget(delete_code_button)

        # Combine panels into the main layout
        layout.addLayout(left_panel, 3)  # Left panel takes 3/4 of the width
        layout.addLayout(right_panel, 1)  # Right panel takes 1/4 of the width

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_file(self):
        """Open a file dialog to load a text file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.setText(content)

    def add_code(self):
        """Add a new code to the code list."""
        # Placeholder: Add logic to prompt for a new code name
        new_code = f"Code {self.code_list.count() + 1}"  # Example: Auto-generate code name
        self.code_list.addItem(new_code)

    def delete_code(self):
        """Delete the selected code from the code list."""
        selected_item = self.code_list.currentItem()
        if selected_item:
            self.code_list.takeItem(self.code_list.row(selected_item))


# Entry point of the application
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())