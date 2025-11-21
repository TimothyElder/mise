import sys
from PySide6.QtWidgets import QApplication
from mise.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setDesktopFileName("Mise")
    app.setApplicationName("Mise")
    app.setOrganizationName("The Dartmouth Institute")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())