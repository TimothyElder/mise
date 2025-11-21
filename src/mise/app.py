import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow

def run():
    app = QApplication(sys.argv)

    app.setDesktopFileName("Mise")
    app.setApplicationName("Mise")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationDomain("https://miseqda.come")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())