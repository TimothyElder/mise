import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon

from .main_window import MainWindow
from .utils.logging_config import setup_logging
from .utils.paths import asset_path


def run():
    setup_logging(Path.home() / ".mise", level=logging.DEBUG)
    app = QApplication(sys.argv)
    
    # with open("src/mise/assets/styles.qss", "r") as f:
    #     _style = f.read()
    #     app.setStyleSheet(_style)

    icon = QIcon(str(asset_path("mise-icon.png")))
    app.setWindowIcon(icon)

    app.setDesktopFileName("Mise")
    app.setApplicationName("Mise")
    app.setApplicationVersion("0.1.2")
    app.setOrganizationDomain("https://miseqda.com")

    app.setOrganizationName("MimirResearch")
    app.setOrganizationDomain("mimirresearch.org")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())