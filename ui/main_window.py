import qdarkstyle
from qdarkstyle.light.palette import LightPalette
import qtawesome as qta

from .icons import *
from .widgets import *
from core import action_manager, ACTION_TOOL_BAR

from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QAction, QVBoxLayout, QWidget, QToolBar, QHBoxLayout, QSizePolicy,QToolButton,
                             QStatusBar, QDockWidget, QListView, QFileDialog, QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("iCell")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))  # Default Dark theme
        self.is_dark_theme = False

        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_central_widget()


    def create_menu_bar(self):
        """Create the menu bar with actions"""
        menubar = self.menuBar()
        
        file_menu = QMenu('File', self)
        new_action = self.create_action('New', M_FILE_NEW_ICON, self.new_file)
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
        circuit_action = self.create_checked_action('Circuit', M_VIEW_CIRCUIT_ICON, self.show_circuit)
        layout_action = self.create_checked_action('Layout', M_VIEW_LAYOUT_ICON, self.show_layout)
        layers_action = self.create_checked_action('Layers', M_VIEW_LAYERS_ICON, self.show_layers)        
        view_menu.addActions([lib_action, circuit_action, layout_action, layers_action])
        action_manager().add_actions(ACTION_TOOL_BAR, [lib_action, circuit_action, layout_action, layers_action])

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
        """Create toolbar with icons"""
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
        """Create central widget for the main layout"""
        self.schematic_view = QDockWidget("Circuit", self)
        self.setCentralWidget(self.schematic_view)

        all_cells = ["Cell1", "Cell2", "Cell3", "Cell4"]
        self.library_browser = LibraryBrowser(all_cells)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library_browser)

        self.view_browser = QDockWidget("View Browser", self)
        tree_widget = QTreeWidget(self.view_browser)
        tree_widget.setHeaderLabels(["Library", "Cell"])
        root = QTreeWidgetItem(tree_widget, ["Library1"])
        QTreeWidgetItem(root, ["Cell1"])
        QTreeWidgetItem(root, ["Cell2"])
        self.view_browser.setWidget(tree_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.view_browser)

        
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

    # Menu functions (currently empty)
    def new_file(self):
        pass

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Spice Files (*.sp);;GDS Files (*.gds;*.gdsII);;LEF Files (*.lef);;DEF Files (*.def);;All Files (*)")
        if file:
            print(f"Opening file: {file}")

    def close_file(self):
        pass

    def save_file(self):
        pass

    def save_as_file(self):
        pass

    def exit_app(self):
        self.close()

    def show_cells(self):
        if self.library_browser.isHidden():
            self.library_browser.show()
        else:
            self.library_browser.hide()

    def show_circuit(self):
        if self.schematic_view.isHidden():
            self.schematic_view.show()
        else:
            self.schematic_view.hide()
        

    def show_layout(self):
        if self.view_browser.isHidden():
            self.view_browser.show()
        else:
            self.view_browser.hide()
    
    def show_layers(self):
        print("Showing Layers")

    def toggle_toolbar(self):
        if self.toolbar.isHidden():
            self.toolbar.show()
        else:
            self.toolbar.hide()
            

    def open_settings(self):
        """Function for 'Settings' button"""
        print("Settings button clicked")

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
        iCell
        Copyright © 2022-2025
        """

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)  # Set the icon type (Information, Warning, Error, etc.)
        msg_box.setWindowTitle("About iCell")  # Set the title of the dialog box
        msg_box.setText(about_message)  # Set the message text
        msg_box.setStandardButtons(QMessageBox.Ok)  # Add an Ok button to close the dialog

        msg_box.exec_()  # Display the dialog
