from PyQt5.QtWidgets import QDockWidget, QListView, QVBoxLayout, QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from core import library_manager, LibraryManager
from .lef_macro_view import LefMacroView

class LibraryBrowser(QDockWidget):
    def __init__(self, macro_view: LefMacroView, parent=None):
        super().__init__("Library Browser", parent=parent)
        self.macro_view = macro_view
        
        self.widget = QWidget(self)
        self.setWidget(self.widget)

        layout = QVBoxLayout(self.widget)
        self.list_view = QListView(self)    
        self.model = QStandardItemModel(self.list_view)    
        self.list_view.setModel(self.model)
        
        self.list_view.setEditTriggers(QListView.NoEditTriggers)
        self.list_view.doubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.list_view)

    
    def setup_models(self, cell_names):
        for name in cell_names:
            item = QStandardItem(name)
            item.setEditable(False)
            self.model.appendRow(item)
    
    def on_item_double_clicked(self, index):
        """Slot function to handle double-click events."""
        if not index.isValid():
            return
        item = self.model.itemFromIndex(index)
        if item:
            self.macro_view.draw_cells([item.text()])
    
    # Observer method, python use duck type
    def update(self):
        print('update LibraryBrowser data')
        self.setup_models(library_manager().get_all_macros())
