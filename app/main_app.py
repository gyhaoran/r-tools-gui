# app/main_app.py

import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()

    def run(self):
        """Run the main application"""
        self.main_window.show()
        sys.exit(self.app.exec_())


def main_entry():
    app = MainApp()
    app.run()
