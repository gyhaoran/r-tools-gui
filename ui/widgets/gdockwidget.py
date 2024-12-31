import sys
import qtawesome as qta
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QVBoxLayout, QPushButton, QWidget, QToolButton
from PyQt5.QtCore import Qt

class GDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)

        # Set a custom widget to the dock
        self.setWidget(self.create_widget())
        
        # Customize the dock's close and toggle view buttons
        self.customize_buttons()

        # Set features (optional)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

    def create_widget(self):
        """Create the content for the dock widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        button = QPushButton("Click me!", widget)
        layout.addWidget(button)
        
        widget.setLayout(layout)
        return widget

    def customize_buttons(self):
        """Customize the default DockWidget buttons."""
        # Access the actions of the dock widget
        toggle_action = self.toggleViewAction()
        
        # Customize toggle button icon
        toggle_action.setIcon(qta.icon('fa.toggle-on'))  # Set a custom icon for toggle button
        
        # Customize close button icon by replacing the default QAction
        close_action = self.findChild(QToolButton)
        if close_action:
            close_action.setIcon(qta.icon('fa.times'))  # Set a custom icon for close button
            close_action.setToolTip("Close Dock")  # Optional: Set tooltip for the close button

        # Optional: Set tooltip for toggle button
        toggle_action.setToolTip("Toggle Dock")

        # Ensure to update the widget
        self.update()
