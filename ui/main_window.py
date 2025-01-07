import qdarkstyle
from qdarkstyle.light.palette import LightPalette
import qtawesome as qta

from .icons import *
from .widgets import *
from .dialogs import *
from core import library_manager, LibraryManager, action_manager, ACTION_TOOL_BAR

from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QAction, QVBoxLayout, QWidget, QToolBar, QHBoxLayout, QSizePolicy,QToolButton,
                             QStatusBar, QDockWidget, QFileDialog, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("iCell")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))  # Default Dark theme
        self.is_dark_theme = False

        self.macro_view = None        
        self.library_browser = None      
        self.schematic_view = None
        self.view_browser = None        
        self.layers = None
        
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_central_widget()
        
    def update_toolbar_status(self):
        pass

    def create_menu_bar(self):
        """Create the menu bar with actions"""
        menubar = self.menuBar()
        
        file_menu = QMenu('File', self)
        new_action = self.create_action('New', M_FILE_NEW_ICON, self.new_project)
        open_action = self.create_action('Open', M_FILE_OPEN_ICON, self.open_file)        
        save_action = self.create_action('Save', M_FILE_SAVE_ICON, self.save_file)
        save_as_aciton = self.create_action('Save As', M_FILE_SAVE_AS_ICON, self.save_as_file)
        close_action = self.create_action('Close', M_FILE_CLOSE_ICON, self.close_file)        
        exit_action = self.create_action('Exit...', M_FILE_EXIT_ICON, self.exit_app)        
                
        file_menu.addActions([new_action, open_action])
        seprator = file_menu.addSeparator()
        file_menu.addActions([save_action, save_as_aciton, close_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        action_manager().add_actions(ACTION_TOOL_BAR, [new_action, open_action, save_action, seprator])

        view_menu = QMenu('View', self)
        lib_action = self.create_checked_action('Library', M_VIEW_LIBRARY_ICON, self.show_cells)
        macro_action = self.create_checked_action('Macro View', M_VIEW_MACRO_VIEW_ICON, self.show_macro_view)
        self.circuit_action = self.create_checked_action('Circuit', M_VIEW_CIRCUIT_ICON, self.show_circuit)
        self.circuit_action.setDisabled(True)        
        self.layout_action = self.create_checked_action('Layout', M_VIEW_LAYOUT_ICON, self.show_layout)
        self.layout_action.setDisabled(True)
        self.layers_action = self.create_checked_action('Layers', M_VIEW_LAYERS_ICON, self.show_layers)
        self.layers_action.setDisabled(True)
        view_actions= [lib_action, macro_action, self.circuit_action, self.layout_action, self.layers_action]
        view_menu.addActions(view_actions)
        action_manager().add_actions(ACTION_TOOL_BAR, view_actions)

        tools_menu = QMenu('Tools', self)
        toolbar_action = self.create_action('ToolBars', M_TOOLS_TOOLBAR_ICON, self.toggle_toolbar)
        tools_menu.addAction(toolbar_action)

        place_menu = QMenu('Place', self)
        global_place_action = self.create_action('Global Place', M_PLACE_GLOBAL_ICON, self.global_place)
        detail_place_action = self.create_action('Detail Place', M_PLACE_DETAIL_ICON, self.global_place)
        place_run_action = self.create_action('Auto Run', M_PLACE_RUN_ICON, self.auto_run)        
        place_menu.addActions([global_place_action, detail_place_action, place_run_action])

        route_menu = QMenu('Route', self)
        global_route_action = self.create_action('Global Route', M_ROUTE_GLOBAL_ICON, self.global_route)
        detail_route_action = self.create_action('Detail Route', M_ROUTE_DETAIL_ICON, self.detail_route)
        route_run_action = self.create_action('Auto Run', M_ROUTE_RUN_ICON, self.auto_run_route)        
        route_menu.addActions([global_route_action, detail_route_action, route_run_action])

        help_menu = QMenu('Help', self)
        about_action = self.create_action('About', M_HELP_ABOUT_ICON, self.show_about)
        help_menu.addAction(about_action)

        menubar.addMenu(file_menu)
        menubar.addMenu(view_menu)
        menubar.addMenu(tools_menu)
        menubar.addMenu(place_menu)
        menubar.addMenu(route_menu)
        menubar.addMenu(help_menu)

    def create_action(self, name, icon, function, checkable=False, checked=False):
        """Helper method to create a menu action with an icon"""
        action = QAction(qta.icon(icon), name, self)
        action.triggered.connect(function)
        action.setCheckable(checkable)
        action.setChecked(checked)
        return action
    
    def create_checked_action(self, name, icon, function, checked=True):
        """Helper method to create a checked menu action with an icon"""
        return self.create_action(name, icon, function, True, checked)

    def create_tool_bar(self):
        self.toolbar = ToolBar(action_manager().get_action(ACTION_TOOL_BAR), parent=self)
        self.addToolBar(self.toolbar)

    def create_status_bar(self):
        """Create a status bar with toggle theme"""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        self.theme_toggle = QPushButton("", self)
        self.theme_toggle.setIcon(qta.icon('fa.toggle-on'))
        self.theme_toggle.setToolTip(self._get_theme_tooltip(self.is_dark_theme))
        self.theme_toggle.clicked.connect(self.switch_theme)
        status_bar.addPermanentWidget(self.theme_toggle)

        status_bar.showMessage("Ready")

    def create_central_widget(self):
        # """Create central widget for the main layout"""
        self.macro_view = LefMacroView()
        self.setCentralWidget(self.macro_view)
        self.setContentsMargins(0,0,0,0)
        library_manager().add_observer(self.macro_view)
        
        self.library_browser = LibraryBrowser(self.macro_view)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_browser)
        library_manager().add_observer(self.library_browser)
        
        # self.schematic_view = Circuit(self)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.schematic_view)

        # self.view_browser = ViewBrowser(self)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.view_browser)
        
        # self.layers = LayersWidget(self)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.layers)
        
    def _get_theme_tooltip(self, is_dark):
        return "Light Mode" if is_dark else "Dark Mode"

    def switch_theme(self):
        """Toggle between dark and light themes"""
        if self.is_dark_theme:
            self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))
        else:
            self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        
        self.is_dark_theme = not self.is_dark_theme
        self.theme_toggle.setToolTip(self._get_theme_tooltip(self.is_dark_theme))
        self.macro_view.set_theme(self.is_dark_theme)

    def new_project(self):
        dialog = NewProjectDialog(self)
        dialog.exec()

    def open_file(self):
        dialog = OpenFileDialog(self)
        dialog.open_file()

    def close_file(self):
        pass

    def save_file(self):
        pass

    def save_as_file(self):
        pass

    def exit_app(self):
        self.close()
        
    def show_widgets(self, widget):
        if widget is None:
            return
        if widget.isHidden():
            widget.show()
        else:
            widget.hide()

    def show_cells(self):
        self.show_widgets(self.library_browser)
        
    def show_macro_view(self):
        self.show_widgets(self.macro_view)

    def show_circuit(self):
        self.show_widgets(self.schematic_view)        

    def show_layout(self):
        self.show_widgets(self.view_browser)
    
    def show_layers(self):
        self.show_widgets(self.layers)

    def toggle_toolbar(self):
        self.show_widgets(self.toolbar)

    def pac_tool(self):
        pass

    def global_place(self):
        pass

    def detail_place(self):
        pass

    def auto_run(self):
        pass

    def global_route(self):
        pass

    def detail_route(self):
        pass

    def auto_run_route(self):
        pass

    def show_about(self):
        """Show About dialog with application information"""
        about_message = """
        r-tools
        Copyright © 2023-2025
        """

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("About iCell")
        msg_box.setText(about_message)
        msg_box.setStandardButtons(QMessageBox.Ok) 

        msg_box.exec_()
