from core import toolbar_manager, ToolBarManager
from PyQt5.QtWidgets import QAction, QToolBar, QHBoxLayout, QSizePolicy, QToolButton


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
    
    def add_actions(self, actions):
        """Add QActions to the group"""
        for action in actions:
            self.add_action(action)

    def add_separator(self):
        """Add a separator at the end of the group."""
        if self.separator:
            return
        self.separator = self.tool_bar.addSeparator()
        self._add_action(self.separator)
    
    def clear(self):
        """Clean toolbar group"""
        self.actions = []  # List to track actions in the group
        self.separator = None  # Reference to the separator (if any)

class ToolBar(QToolBar):

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.groups = {}  # Store groups in insertion order
        toolbar_manager().add_observer(self)

    def add_group(self, name)-> ToolBarGroup:
        """Add a new toolbar group."""
        if name not in self.groups:
            group = ToolBarGroup(name, self)
            self.groups[name] = group
        return self.groups[name]

    def get_group(self, name):
        """Get the toolbar group with the specified name."""
        return self.groups.get(name)
    
    def clear(self):
        """Clean toolbar and groups"""
        super().clear()
        for _, group in self.groups.items():
            group.clear()
    
    def update(self):
        self.clear()
        for i, (key, group) in enumerate(self.groups.items()):
            actions = toolbar_manager().get_actions(key)
            group.add_actions(actions)
            if i < len(self.groups) - 1:
                group.add_separator()
