import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from .main_window import MainWindow
from .utils.logging_config import setup_logging
from .utils.paths import asset_path

def run():
    setup_logging(Path.home() / ".mise", level=logging.DEBUG)
    app = QApplication(sys.argv)

    icon = QIcon(str(asset_path("mise-icon.png")))
    app.setWindowIcon(icon)

    app.setDesktopFileName("Mise")
    app.setApplicationName("Mise")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationDomain("https://miseqda.come")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())