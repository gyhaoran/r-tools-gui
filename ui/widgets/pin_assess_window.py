from ui.dialogs import *
from core.window import AbstractWindow, W_PIN_ASSESS_ID

from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout
)
from PyQt5.QtCore import Qt


class PinAssessWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Pin Assessment", parent)
        self._setup_ui()
        self.setMinimumWidth(200)
        self.setMaximumWidth(600)

    def _setup_ui(self):
        # Create a central widget to hold the layout
        self.central_widget = QWidget(self)
        self.setWidget(self.central_widget)

        # Create a vertical layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Set the layout to the central widget
        self.central_widget.setLayout(self.main_layout)

        # Initialize placeholders for the dialogs
        self.macro_score_dialog = None
        self.pin_score_dialog = None
        self.pin_destiny_dialog = None

    def _load_macro_score(self, data):
        """Load MacroScoreDialog content."""
        self.macro_score_dialog = MacroScoreDialog(data, self)
        self.main_layout.addWidget(self.macro_score_dialog)

    def _load_pin_score(self, data):
        """Load PinScoreDialog content."""
        self.pin_score_dialog = PinScoreDialog(data, self)
        self.main_layout.addWidget(self.pin_score_dialog)

    def _load_pin_destiny(self, data):
        """Load PinDestinyDialog content."""
        self.pin_destiny_dialog = PinDestinyDialog(data, self)
        self.main_layout.addWidget(self.pin_destiny_dialog)

    def _clear_macro_score(self):
        """Clear MacroScoreDialog content."""
        if self.macro_score_dialog:
            self.main_layout.removeWidget(self.macro_score_dialog)
            self.macro_score_dialog.deleteLater()
            self.macro_score_dialog = None

    def _clear_pin_score(self):
        """Clear PinScoreDialog content."""
        if self.pin_score_dialog:
            self.main_layout.removeWidget(self.pin_score_dialog)
            self.pin_score_dialog.deleteLater()
            self.pin_score_dialog = None

    def _clear_pin_destiny(self):
        """Clear PinDestinyDialog content."""
        if self.pin_destiny_dialog:
            self.main_layout.removeWidget(self.pin_destiny_dialog)
            self.pin_destiny_dialog.deleteLater()
            self.pin_destiny_dialog = None

    def clear(self):
        """Clear all loaded content."""
        self._clear_macro_score()
        self._clear_pin_score()
        self._clear_pin_destiny()
    
    def load(self, pin_destiny_data, macro_score_data, pin_score_data):
        """Load all pin score"""
        self.clear()
        self._load_pin_score(pin_score_data)
        self._load_macro_score(macro_score_data)
        self._load_pin_destiny(pin_destiny_data)


class PinAssessWindow(AbstractWindow):
    def __init__(self, parent=None):
        super().__init__(W_PIN_ASSESS_ID)
        self._widget = PinAssessWidget(parent)
    
    def widget(self):
        return self._widget
    
    def area(self):
        return Qt.RightDockWidgetArea
     
    def is_center(self):
        return False
    
    def load(self, pin_destiny_data, macro_score_data, pin_score_data):
        self._widget.load(pin_destiny_data, macro_score_data, pin_score_data)
    
    def clear(self):
        self._widget.clear()
        