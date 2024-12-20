from PySide6.QtWidgets import QApplication
from mise.main_window import MainWindow  # Import your MainWindow class

if __name__ == "__main__":
    app = QApplication([])

    # Set the application name and organization
    app.setDesktopFileName("Mise")
    app.setApplicationName("Mise")
    app.setOrganizationName("The Dartmouth Institute")  # Optional: Use your organization or leave it generic

    window = MainWindow()
    window.show()
    app.exec()