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

    def get_settings(self):
        return {
            "theme": self.theme_combo.text(),
            "language": self.language_combo.text(),
            "auto_save": self.auto_save_checkbox.isChecked(),
        }
