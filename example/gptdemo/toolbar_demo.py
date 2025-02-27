from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QToolBar, QAction
)
from PyQt5.QtCore import Qt
import qtawesome as qta  # Use qtawesome for icons


class ToolBarGroup():
    """Encapsulate a toolbar group with support for actions and separators."""

    def __init__(self, name, tool_bar):
        self.name = name  # Group name
        self.tool_bar = tool_bar  # Parent QToolBar
        self.actions = []  # List to track actions in the group
        self.separator = None  # Reference to the separator (if any)
        
    def _get_next_action(self, action):
        current_actions = self.tool_bar.actions()
        try:
            current_idx = current_actions.index(action)
            next_idx = current_idx + 1
            next_action = current_actions[next_idx] if next_idx < len(current_actions) else None
        except ValueError:
            next_action = None
        return next_action

    def _add_action(self, action):
        if self.actions:  # Insert after the last action
            next_action = self._get_next_action(self.actions[-1])
            self.tool_bar.insertAction(next_action, action)
        else: # If the group is empty, add the action directly
            self.tool_bar.addAction(action)

    def add_action(self, action):
        """Add a QAction to the group, ensuring it appears before any separator."""
        if self.separator:
            self.tool_bar.insertAction(self.separator, action)
        else:
            self._add_action(action)
        self.actions.append(action)

    def add_separator(self):
        """Add a separator at the end of the group."""
        if self.separator:
            return        
        self.separator = self.tool_bar.addSeparator()
        self._add_action(self.separator)

class CustomToolBar(QToolBar):
    """Custom QToolBar with group management support."""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.groups = {}  # Store groups in insertion order

    def add_group(self, name):
        """Add a new toolbar group."""
        if name not in self.groups:
            group = ToolBarGroup(name, self)
            self.groups[name] = group
        return self.groups[name]

    def get_group(self, name):
        """Get the toolbar group with the specified name."""
        return self.groups.get(name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom ToolBar with Groups Example")
        self.setGeometry(100, 100, 800, 600)

        # Create MenuBar
        self._create_menu_bar()

        # Create Custom ToolBar
        self._create_custom_tool_bar()

        # Simulate plugin adding actions
        self._simulate_plugin_actions()

    def _create_menu_bar(self):
        """Create the MenuBar and add menus with actions."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")
        self.new_action = QAction(qta.icon("fa.file"), "New", self)
        self.open_action = QAction(qta.icon("fa.folder-open"), "Open", self)
        self.save_action = QAction(qta.icon("fa.save"), "Save", self)
        file_menu.addActions([self.new_action, self.open_action, self.save_action])

        # View Menu
        view_menu = menu_bar.addMenu("View")
        self.zoom_in_action = QAction(qta.icon("fa.search-plus"), "Zoom In", self)
        self.zoom_out_action = QAction(qta.icon("fa.search-minus"), "Zoom Out", self)
        view_menu.addActions([self.zoom_in_action, self.zoom_out_action])

        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")
        self.cut_action = QAction(qta.icon("fa.scissors"), "Cut", self)
        self.copy_action = QAction(qta.icon("fa.copy"), "Copy", self)
        self.paste_action = QAction(qta.icon("fa.paste"), "Paste", self)
        tools_menu.addActions([self.cut_action, self.copy_action, self.paste_action])

    def _create_custom_tool_bar(self):
        """Create the Custom ToolBar and add initial groups."""
        self.tool_bar = CustomToolBar("Main ToolBar", self)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

        # Add groups in the desired order: File → View → Tools
        self.file_group = self.tool_bar.add_group("File")
        self.file_group.add_action(self.new_action)
        self.file_group.add_action(self.open_action)
        self.file_group.add_action(self.save_action)
        self.file_group.add_separator()

        self.view_group = self.tool_bar.add_group("View")
        self.view_group.add_action(self.zoom_in_action)
        self.view_group.add_action(self.zoom_out_action)
        self.view_group.add_separator()

        self.tools_group = self.tool_bar.add_group("Tools")
        self.tools_group.add_action(self.cut_action)
        self.tools_group.add_action(self.copy_action)
        self.tools_group.add_action(self.paste_action)

    def _simulate_plugin_actions(self):
        """Simulate plugins adding actions to specific groups."""
        # Plugin 1: Add to File group (appears after "Save")
        plugin_action_1 = QAction(qta.icon("fa.plug"), "Plugin Action 1", self)
        self.file_group.add_action(plugin_action_1)
        
        plugin_action_2 = QAction(qta.icon("fa.plug"), "Plugin Action 2", self)
        self.file_group.add_action(plugin_action_2)
        self.file_group.add_separator()
        plugin_action_3 = QAction(qta.icon("fa.plug"), "Plugin Action 3", self)
        self.file_group.add_action(plugin_action_3)

        # Plugin 2: Add to Tools group (appears after "Paste")
        plugin_action_4 = QAction(qta.icon("fa.wrench"), "Plugin Action 4", self)
        self.tools_group.add_action(plugin_action_4)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())