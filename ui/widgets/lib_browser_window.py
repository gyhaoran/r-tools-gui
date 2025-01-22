import qtawesome as qta
from .lef_macro_window import LefMacroWindow
from .pin_assess_window import PinAssessWindow
from core import library_manager
from core.window import AbstractWindow, W_LIB_BROWSER_ID
from ui.dialogs import MacroScoreDialog, PinScoreDialog, MacroInfoDialog, PinDestinyDialog

from PyQt5.QtWidgets import QDockWidget, QListView, QVBoxLayout, QWidget, QMenu, QAction
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


class LibBrowserWidget(QDockWidget):
    def __init__(self, macro_win: LefMacroWindow, pin_assess_win: PinAssessWindow, parent=None):
        super().__init__("Macro Browser", parent=parent)
        self.macro_win = macro_win
        self.pin_assess_win = pin_assess_win

        self.action_handlers = {
            "Copy Name": self.copy_name,
            "Calc Macro Score": self.calc_macro_score,
            "Calc Pin Score": self.calc_pin_score,
            "Calc Pin Destiny": self.calc_pin_destiny,
            "Show Details": self.show_macro_infos,
        }

        self.init_ui()

    def init_ui(self):
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
        self.setMinimumWidth(200)
        self.setMaximumWidth(350)

    def setup_models(self, cell_names):
        """Setup the model with the given cell names."""
        self.model.clear()
        for name in cell_names:
            item = QStandardItem(name)
            item.setEditable(False)
            self.model.appendRow(item)

    def on_item_double_clicked(self, index):
        if not index.isValid():
            return
        item = self.model.itemFromIndex(index)
        if item:
            macro_name = item.text()
            self.macro_win.draw_cells([macro_name])
            self.pin_assess_win.load(library_manager().calc_pin_density(macro_name), 
                                      library_manager().calc_macro_score(macro_name),
                                      library_manager().calc_pin_score(macro_name))

    def show_context_menu(self, position):
        """Show a context menu at the given position."""
        index = self.list_view.indexAt(position)
        if not index.isValid():
            return

        menu = self.create_context_menu()
        action = menu.exec_(self.list_view.mapToGlobal(position))
        self.handle_context_menu_action(action, index)

    def create_context_menu(self):
        menu = QMenu(self.list_view)
        copy_name_action = QAction(qta.icon('msc.copy'), "Copy Name", self)
        macro_score_action = QAction(qta.icon('msc.type-hierarchy'), "Calc Macro Score", self)
        pin_score_action = QAction(qta.icon('msc.pin'), "Calc Pin Score", self)
        pin_destiny_action = QAction(qta.icon('msc.pinned'), "Calc Pin Destiny", self)
        show_infos_action = QAction(qta.icon('msc.info'), 'Show Details', self)

        menu.addActions([macro_score_action, pin_score_action, pin_destiny_action])
        menu.addSeparator()
        menu.addActions([copy_name_action, show_infos_action])
        return menu

    def handle_context_menu_action(self, action, index):
        """Handle the selected action from the context menu."""
        if not action or not index.isValid():
            return

        item = self.model.itemFromIndex(index)
        if not item:
            return

        macro_name = item.text()
        self.execute_action(action.text(), macro_name)

    def execute_action(self, action_name, macro_name):
        """Execute the action based on the action name."""
        handler = self.action_handlers.get(action_name)
        if handler:
            handler(macro_name)

    def copy_name(self, macro_name):
        clipboard = QApplication.clipboard()
        clipboard.setText(macro_name)

    def calc_macro_score(self, macro_name):
        data = library_manager().calc_macro_score(macro_name)
        dialog = MacroScoreDialog(data, self)
        dialog.exec_()

    def calc_pin_score(self, macro_name):
        data = library_manager().calc_pin_score(macro_name)
        dialog = PinScoreDialog(data, self)
        dialog.exec_()

    def calc_pin_destiny(self, macro_name):
        data = library_manager().calc_pin_density(macro_name)
        dialog = PinDestinyDialog(data, self)
        dialog.exec_()

    def show_macro_infos(self, macro_name):
        macro = library_manager().get_macro_info(macro_name)
        dialog = MacroInfoDialog(macro, self)
        dialog.exec_()

    def update(self):
        self.setup_models(library_manager().get_all_macros())
        self.pin_assess_win.clear()


class LibBrowserWindow(AbstractWindow):
    def __init__(self, macro_win: LefMacroWindow, pin_assess_win: PinAssessWindow, parent=None):
        super().__init__(W_LIB_BROWSER_ID)
        self._widget = LibBrowserWidget(macro_win, pin_assess_win, parent)
        library_manager().add_observer(self._widget)
    
    def widget(self):
        return self._widget
    
    def area(self):
        return Qt.LeftDockWidgetArea
    
    def is_center(self):
        return False
        
    def calc_macro_score(self, macro_name):
        self._widget.calc_macro_score(macro_name)

    def calc_pin_score(self, macro_name):
        self._widget.calc_pin_score(macro_name)

    def calc_pin_destiny(self, macro_name):
        self._widget.calc_pin_destiny(macro_name)    
