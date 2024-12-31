# ui/side_panels.py

from PyQt5.QtWidgets import QDockWidget, QListView, QTreeWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class SidePanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Side Panel")

        # Set up the layout for the side panel
        self.layout = QVBoxLayout()
        
        self.list_view = QListView()
        self.tree_widget = QTreeWidget()
        self.layout.addWidget(self.list_view)
        self.layout.addWidget(self.tree_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setWidget(central_widget)
