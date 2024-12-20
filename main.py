from PySide6.QtWidgets import QApplication
from mise.main_window import MainWindow  # Import your MainWindow class

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()