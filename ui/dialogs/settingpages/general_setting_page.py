from ui.icons import M_TOOLS_SETTINGS_ICON
from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QCheckBox,
    QFormLayout
)

class GeneralSettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout(self)
        self.theme_combo = QLineEdit("Light")
        layout.addRow("Theme:", self.theme_combo)
        self.language_combo = QLineEdit("English")
        layout.addRow("Language:", self.language_combo)
        self.auto_save_checkbox = QCheckBox("Enable Auto Save")
        layout.addRow(self.auto_save_checkbox)
        
    def save(self):
        pass

    def has_modified(self)-> bool:
        return False

    def get_setting(self):
        return {"general": {"theme": self.theme_combo.text()}}

    def title(self):
        return "General Settings"
    
    def icon(self):
        return M_TOOLS_SETTINGS_ICON
