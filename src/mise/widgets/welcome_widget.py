from pathlib import Path
import logging
logger = logging.getLogger(__name__)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
    )

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

from ..utils.paths import asset_path

class WelcomeWidget(QWidget):
    """
    Sets up the welcome widget in the main window with the create and open projects buttons,
    and basic welcome information and branding.

    Usage:
    welcome = WelcomeWidget(on_new_project=self.create_new_project, on_open_project=self.open_project)
    """
    new_project_requested = Signal()
    open_project_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        # ----- LEFT: buttons -----
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)

        create_button = QPushButton("Create New Project")
        create_button.clicked.connect(self.new_project_requested)
        open_button = QPushButton("Open Project")
        open_button.clicked.connect(self.open_project_requested)

        button_layout.addWidget(create_button)
        button_layout.addWidget(open_button)
        button_layout.setAlignment(Qt.AlignCenter)
        button_container.setFixedWidth(220)
        layout.addWidget(button_container)

        # Logo Widget (Center)
        logo_label = QLabel()
        pixmap = QPixmap(asset_path("mise.png")).scaled(
            500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        logo_label.setFixedWidth(500)
        logo_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        layout.addWidget(logo_label, stretch=0)
        
        # Software Description (Right Side)
        right_container = QWidget()
        logo_layout = QVBoxLayout(right_container)

        description_label = QLabel()
        description_label.setText("""<p style="font-size: 14px; color: grey;">Mise ("<em>meez</em>") is an qualitative data analysis tool designed to place good principles at the heart of software.</p>
               <p>There are a few principles that guide this software:</p>
               <ul>
                    <li>Codes should be applied to large chunks of text</li>
                    <li>Everything should be accessible to the analyst</li>
                    <li>Anlaysis should be made as transparent as possible</li>
               </ul>

                <p>Suggestions or bugs can be reported to <a href='mailto:timothy.b.elder@dartmouth.edu'>timothy.b.elder@dartmouth.edu</a></p>

                <p><a href='https://miseqda.com'>miseqda.com</a></p>
            """)
        description_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        description_label.setWordWrap(True)

        # Let this one expand horizontally
        description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Optional: cap width so it doesn’t become a mile-long line
        description_label.setMaximumWidth(400)

        logo_layout.addWidget(description_label)

        layout.addWidget(right_container, stretch=1)
