import os
import qdarkstyle
from qdarkstyle.light.palette import LightPalette
import qtawesome as qta
from .icons import *
from .widgets import *
from .dialogs import *
from core import *
from plugins.pac_plugin.ui.dialogs import *

from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QAction, QVBoxLayout, QWidget, QToolBar, QStatusBar, QDockWidget, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon


class MainWindow(QMainWindow):
    theme_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iCell")
        icon_file = os.path.realpath(os.path.dirname(__file__) + f'/icons/image/{MAIN_WINDOW_ICON}')
        self.setWindowIcon(QIcon(icon_file))
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))
        self.is_dark_theme = False
        
        self._init_manager()
        
        self.schematic_view = None
        self.view_browser = None
        self.layers = None

        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        
    def _init_manager(self):
        create_menu_manager(self.menuBar())

    def create_menu_bar(self):
        file_menu = self.create_file_menu()
        view_menu = self.create_view_menu()
        tools_menu = self.create_tools_menu()
        place_menu = self.create_place_menu()
        route_menu = self.create_route_menu()
        help_menu = self.create_help_menu()
        
        menu_manager().add_menu(M_FILE_ID, file_menu)
        menu_manager().add_menu(M_VIEW_ID, view_menu)
        menu_manager().add_menu(M_TOOLS_ID, tools_menu)
        menu_manager().add_menu(M_PLACE_ID, place_menu)
        menu_manager().add_menu(M_ROUTE_ID, route_menu)
        menu_manager().add_menu(M_HELP_ID, help_menu)

    def create_help_menu(self):
        help_menu = QMenu('Help', self)
        about_action = self.create_action('About', M_HELP_ABOUT_ICON, self.show_about)
        help_menu.addAction(about_action)
        return help_menu

    def create_route_menu(self):
        route_menu = QMenu('Route', self)
        global_route_action = self.create_action('Global Route', M_ROUTE_GLOBAL_ICON, self.global_route)
        detail_route_action = self.create_action('Detail Route', M_ROUTE_DETAIL_ICON, self.detail_route)
        route_run_action = self.create_action('Auto Run', M_ROUTE_RUN_ICON, self.auto_run_route)
        route_menu.addActions([global_route_action, detail_route_action, route_run_action])
        return route_menu

    def create_place_menu(self):
        place_menu = QMenu('Place', self)
        global_place_action = self.create_action('Global Place', M_PLACE_GLOBAL_ICON, self.global_place)
        detail_place_action = self.create_action('Detail Place', M_PLACE_DETAIL_ICON, self.global_place)
        place_run_action = self.create_action('Auto Run', M_PLACE_RUN_ICON, self.auto_run)
        place_menu.addActions([global_place_action, detail_place_action, place_run_action])
        return place_menu

    def create_tools_menu(self):
        tools_menu = QMenu('Tools', self)
        toolbar_action = self.create_action('ToolBars', M_TOOLS_TOOLBAR_ICON, self.toggle_toolbar)
        tools_menu.addAction(toolbar_action)
        tools_menu.addSeparator()
        settings_action = self.create_action('Settings', M_TOOLS_SETTINGS_ICON, self.show_settings)
        tools_menu.addAction(settings_action)
        return tools_menu

    def create_view_menu(self):
        view_menu = QMenu('View', self)
        self.circuit_action = self.create_checked_action('Circuit', M_VIEW_CIRCUIT_ICON, self.show_circuit)
        self.circuit_action.setDisabled(True)
        self.layout_action = self.create_checked_action('Layout', M_VIEW_LAYOUT_ICON, self.show_layout)
        self.layout_action.setDisabled(True)
        self.layers_action = self.create_checked_action('Layers', M_VIEW_LAYERS_ICON, self.show_layers)
        self.layers_action.setDisabled(True)

        view_actions = [self.circuit_action, self.layout_action, self.layers_action]
        view_menu.addActions(view_actions)
        view_menu.addSeparator()
        toolbar_manager().add_actions(TOOLBAR_VIEW, view_actions)
        return view_menu

    def create_file_menu(self):
        file_menu = QMenu('File', self)
        new_action = self.create_action('New', M_FILE_NEW_ICON, self.new_project)
        open_action = self.create_action('Open', M_FILE_OPEN_ICON, self.open_file)
        save_action = self.create_action('Save', M_FILE_SAVE_ICON, self.save_file)
        save_as_action = self.create_action('Save As', M_FILE_SAVE_AS_ICON, self.save_as_file)
        close_action = self.create_action('Close', M_FILE_CLOSE_ICON, self.close_file)
        exit_action = self.create_action('Exit...', M_FILE_EXIT_ICON, self.exit_app)

        file_menu.addActions([new_action, open_action])
        file_menu.addSeparator()
        file_menu.addActions([save_action, save_as_action, close_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        toolbar_manager().add_actions(TOOLBAR_FILE, [new_action, open_action, save_action])
        return file_menu

    def create_action(self, name, icon, function, checkable=False, checked=False):
        action = QAction(qta.icon(icon), name, self)
        action.triggered.connect(function)
        action.setCheckable(checkable)
        action.setChecked(checked)
        return action

    def create_checked_action(self, name, icon, function, checked=True):
        return self.create_action(name, icon, function, True, checked)

    def create_tool_bar(self):
        self.tool_bar = ToolBar("Main ToolBar", self)
        self.tool_bar.add_group(TOOLBAR_FILE)
        self.tool_bar.add_group(TOOLBAR_VIEW)
        self.tool_bar.add_group(TOOLBAR_TOOLS)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

    def create_status_bar(self):
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        self.theme_toggle = QPushButton("", self)
        self.theme_toggle.setIcon(qta.icon('fa.toggle-on'))
        self.theme_toggle.setToolTip(self._get_theme_tooltip(self.is_dark_theme))
        self.theme_toggle.clicked.connect(self.switch_theme)
        status_bar.addPermanentWidget(self.theme_toggle)

    def show(self):
        window_manager().show_all_windows(self)
        super().show()
        
    def _get_theme_tooltip(self, is_dark):
        return "Light Mode" if is_dark else "Dark Mode"

    def switch_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))
        else:
            self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

        self.is_dark_theme = not self.is_dark_theme
        self.theme_toggle.setToolTip(self._get_theme_tooltip(self.is_dark_theme))
        self.theme_changed.emit(self.is_dark_theme)

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

    def show_circuit(self):
        self.show_widgets(self.schematic_view)

    def show_layout(self):
        self.show_widgets(self.view_browser)

    def show_layers(self):
        self.show_widgets(self.layers)

    def toggle_toolbar(self):
        self.show_widgets(self.toolbar)

    def show_settings(self, index=0):
        dialog = SettingsDialog(self, tab_index=index)
        dialog.exec_()

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
        about_message = """
        r-tools
        Copyright © 2023-2025
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("About r-tools")
        msg_box.setText(about_message)
        msg_box.setStandardButtons(QMessageBox.Ok)

        msg_box.exec_()

    def closeEvent(self, event):
        setting_manager().save_settings()
        event.accept()
