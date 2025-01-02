from PyQt5.QtWidgets import QAction, QToolBar, QHBoxLayout, QSizePolicy, QToolButton


class ToolBar(QToolBar):

    def __init__(self, actions, parent=None):
        super().__init__(parent=parent)        
        self.setup_ui(actions)
    
    def setup_ui(self, actions):
        self.addActions(actions)
