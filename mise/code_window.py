from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QInputDialog, QMessageBox, QToolBar, QListWidget
)
from PySide6.QtGui import QAction
import os


class CodeWindow(QMainWindow):
    """
    A Code Manager window that integrates with the CodeManager class.
    """
    def __init__(self, code_manager):
        super().__init__()
        self.code_manager = code_manager  # Pass an instance of CodeManager
        self.setWindowTitle("Code Manager")
        self.resize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Toolbar
        self.toolbar = QToolBar("Code Manager Toolbar")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.setup_toolbar()

        # Code list view
        self.code_list = QListWidget()
        main_layout.addWidget(self.code_list)

        # Load existing codes into the list
        self.populate_code_list()

    def setup_toolbar(self):
        """
        Set up the toolbar with actions.
        """
        add_action = QAction("Add Code", self)
        add_action.triggered.connect(self.add_code)
        self.toolbar.addAction(add_action)

        delete_action = QAction("Delete Code", self)
        delete_action.triggered.connect(self.delete_code)
        self.toolbar.addAction(delete_action)

        update_action = QAction("Update Code", self)
        update_action.triggered.connect(self.update_code)
        self.toolbar.addAction(update_action)

        save_action = QAction("Save Codes", self)
        save_action.triggered.connect(self.save_codes)
        self.toolbar.addAction(save_action)

        load_action = QAction("Load Codes", self)
        load_action.triggered.connect(self.load_codes)
        self.toolbar.addAction(load_action)

    def populate_code_list(self):
        """
        Populate the QListWidget with codes from the CodeManager.
        """
        self.code_list.clear()
        for name, description in self.code_manager.get_all_codes().items():
            self.code_list.addItem(f"{name}: {description}")

    def add_code(self):
        """
        Add a new code through a dialog.
        """
        name, ok = QInputDialog.getText(self, "Add Code", "Enter code name:")
        if not ok or not name.strip():
            return
        description, ok = QInputDialog.getText(self, "Add Code", "Enter code description:")
        if not ok:
            return
        try:
            self.code_manager.add_code(name.strip(), description.strip())
            self.populate_code_list()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_code(self):
        """
        Delete a selected code.
        """
        selected_item = self.code_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "No code selected.")
            return
        name = selected_item.text().split(":")[0]
        try:
            self.code_manager.delete_code(name)
            self.populate_code_list()
        except KeyError as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_code(self):
        """
        Update the description of a selected code.
        """
        selected_item = self.code_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "No code selected.")
            return
        name = selected_item.text().split(":")[0]
        new_description, ok = QInputDialog.getText(self, "Update Code", f"Enter new description for '{name}':")
        if not ok or not new_description.strip():
            return
        try:
            self.code_manager.update_code(name, new_description.strip())
            self.populate_code_list()
        except KeyError as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_codes(self):
        """
        Save codes to a file.
        """
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Codes", "", "JSON Files (*.json);;CSV Files (*.csv);;Pickle Files (*.pkl)")
        if not filepath:
            return
        try:
            self.code_manager.save_codes(filepath)
            QMessageBox.information(self, "Success", "Codes saved successfully.")
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_codes(self):
        """
        Load codes from a file.
        """
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Codes", "", "JSON Files (*.json);;CSV Files (*.csv);;Pickle Files (*.pkl)")
        if not filepath:
            return
        try:
            loaded_codes = self.code_manager.load_codes(filepath)
            self.code_manager.codes = loaded_codes  # Replace the current codes
            self.populate_code_list()
            QMessageBox.information(self, "Success", "Codes loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))