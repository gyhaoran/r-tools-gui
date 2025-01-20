# app/main_app.py

import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from plugins import PluginManager

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        self.plugin_manager = PluginManager(self.main_window)

    def run(self):
        """Run the main application"""
        self.plugin_manager.load_plugins()
        self.main_window.show()
        sys.exit(self.app.exec_())


def main_entry():
    app = MainApp()
    app.run()
