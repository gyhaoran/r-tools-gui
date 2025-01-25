from core.window import SettingPageRegistor, SettingPageId
from ui.icons import M_TOOLS_SETTINGS_ICON
from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QFormLayout
)
from PyQt5.QtCore import pyqtSignal, QObject

class GeneralSettingsWidget(QWidget):
    change_theme = pyqtSignal(bool)
    DEFAULT_SEETINGS = {"theme": "Light"}
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._general = settings.get('general', self.DEFAULT_SEETINGS)
        self._setup_ui()
        self.theme_combo.setCurrentText(self._general.get('theme', 'Light'))
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setEditable(False)
        self.theme_combo.currentTextChanged.connect(self._change_theme)
        layout.addRow("Theme:", self.theme_combo)
    
    def _is_dark(self)-> bool:
        return self.theme_combo.currentText() == "Dark"
    
    def _change_theme(self):
        self.change_theme.emit(self._is_dark())
        
    def get_setting(self):
        return {"general": {"theme": self.theme_combo.currentText()}}
            
class GeneralSettingsPage(SettingPageRegistor, QObject):
    theme_changed = pyqtSignal(bool)
    
    def __init__(self, settings, parent=None):
        SettingPageRegistor.__init__(self, SettingPageId.GENERAL_SETTING_ID)
        QObject.__init__(self, parent)
        self._widget = GeneralSettingsWidget(settings, parent)
        self._widget.change_theme.connect(self.theme_changed.emit)


    def save(self):
        pass
    
    def widget(self):
        return self._widget

    def has_modified(self)-> bool:
        return False

    def get_setting(self):
        return self._widget.get_setting()

    def title(self):
        return "General Settings"
    
    def icon(self):
        return M_TOOLS_SETTINGS_ICON
