from PyQt5.QtWidgets import QDockWidget, QListView, QVBoxLayout, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class LibraryBrowser(QDockWidget):
    def __init__(self, cell_names, parent=None):
        super().__init__("Library Browser", parent)

        # Initialize the widget
        self.widget = QWidget(self)
        self.setWidget(self.widget)

        # Create a layout to hold the list view
        layout = QVBoxLayout(self.widget)
        
        # Create a QListView to display cell names
        self.list_view = QListView(self)
        
        # Create a model to hold the cell names
        self.model = QStandardItemModel(self.list_view)

        # Add each cell name as an item in the model
        for name in cell_names:
            item = QStandardItem(name)  # Create a new item for each name
            self.model.appendRow(item)   # Add the item to the model
        
        # Set the model to the list view
        self.list_view.setModel(self.model)

        # Add the list view to the layout
        layout.addWidget(self.list_view)
        