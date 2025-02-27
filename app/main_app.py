import sys
from ui import MainWindow
from plugins import PluginManager
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTextCodec

class MainApp():
    def __init__(self):
        self.app = QApplication(sys.argv)
        QTextCodec.setCodecForLocale(QTextCodec.codecForName('UTF-8'))
        self.app.setApplicationName('iCell')            
        self.main_window = MainWindow(self.app)
        self.plugin_manager = PluginManager(self.main_window)
    
    def run(self):
        """Run the main application"""
        self.plugin_manager.load_plugins()
        self.main_window.show()
        sys.exit(self.app.exec_())


def main_entry():
    app = MainApp()
    app.run()
