import pacpy
import json
import os
import qtawesome as qta
from .lef_macro_view import LefMacroView
from core import library_manager, LibraryManager
from ui.dialogs import MacroScoreDialog, PinScoreDialog, MacroInfoDialog, PinDestinyDialog
from PyQt5.QtWidgets import QApplication, QDockWidget, QListView, QVBoxLayout, QWidget, QMenu, QAction
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

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
        
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)
                
        layout.addWidget(self.list_view)

    
    def setup_models(self, cell_names):
        self.model.clear()
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
    
    def show_context_menu(self, position):
        index = self.list_view.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self.list_view)

        copy_name_action = QAction(qta.icon('msc.copy'), "Copy Name", self)
        macro_score_action = QAction(qta.icon('msc.type-hierarchy'), "Calc Macro Score", self)
        pin_score_action = QAction(qta.icon('msc.pin'), "Calc Pin Score", self)
        pin_destiny_action = QAction(qta.icon('msc.pinned'), "Calc Pin Detiny", self)
        show_infos = QAction(qta.icon('msc.info'), 'Show Details', self)

        menu.addAction(copy_name_action)
        menu.addSeparator()
        menu.addActions([macro_score_action, pin_score_action, pin_destiny_action])
        menu.addSeparator()
        menu.addAction(show_infos)

        action = menu.exec_(self.list_view.mapToGlobal(position))

        if action == copy_name_action:
            self.copy_name(index)
        elif action == macro_score_action:
            self.calc_macro_score(index)
        elif action == pin_score_action:
            self.calc_pin_score(index)
        elif action == pin_destiny_action:
            self.calc_pin_destiny(index)
        elif action == show_infos:
            self.show_macro_infos(index)

    def copy_name(self, index):
        item = self.model.itemFromIndex(index)
        if item:
            clipboard = QApplication.clipboard()
            clipboard.setText(item.text())            

    def calc_macro_score(self, index):
        item = self.model.itemFromIndex(index)
        if item:
            macro_name = item.text()
            score = library_manager().calc_macro_score(macro_name)
            data = {macro_name: score}
            dialog = MacroScoreDialog(data, self)
            dialog.exec_()

    def calc_pin_score(self, index):
        item = self.model.itemFromIndex(index)
        if item:
            macro_name = item.text()
            score = library_manager().calc_pin_score(macro_name)
            data = {macro_name: score}
            dialog = PinScoreDialog(data, self)
            dialog.exec_()

    def calc_pin_destiny(self, index):
        item = self.model.itemFromIndex(index)
        if item:
            macro_name = item.text()
            data = library_manager().calc_pin_density(macro_name)
            dialog = PinDestinyDialog(data, self)
            dialog.exec_()

    def show_macro_infos(self, index):
        item = self.model.itemFromIndex(index)
        if item:
            macro = library_manager().get_macro_info(item.text())
            dialog = MacroInfoDialog(macro, self)
            dialog.exec_()
               
    # Observer method, python use duck type
    def update(self):
        self.setup_models(library_manager().get_all_macros())
