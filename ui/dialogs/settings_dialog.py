from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QFormLayout,
    QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import qtawesome as qta
from .settingpages import *
from ui.icons import *


class SettingsDialog(QDialog):
    def __init__(self, parent=None, initial_tab_index=0):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)


        self.general_tab = GeneralSettingsPage(self)
        self.tabs.addTab(self.general_tab, "General Settings")
        self.tabs.setTabIcon(0, qta.icon(M_TOOLS_SETTINGS_ICON))

        self.pin_rule_tab = PinAssessRulePage(self)
        self.tabs.addTab(self.pin_rule_tab, "Pin Assessment Rule")
        self.tabs.setTabIcon(1, qta.icon(M_TOOLS_PIN_RULE_ICON))

        self.drc_rule_tab = DrcRulePage(self)
        self.tabs.addTab(self.drc_rule_tab, "DRC Design Rule")
        self.tabs.setTabIcon(2, qta.icon(M_TOOLS_DRC_RULE_ICON))


        self.tabs.setCurrentIndex(initial_tab_index)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
    def save_settings(self):
        """save settings"""
        general_settings = self.general_tab.get_settings()
        print("General Settings:", general_settings)

        pin_rule_settings = self.pin_rule_tab.get_settings()
        print("Pin Assessment Rule Settings:", pin_rule_settings)

        drc_rule_settings = self.drc_rule_tab.get_settings()
        print("DRC Design Rule Settings:", drc_rule_settings)

        QMessageBox.information(self, "Saved", "Settings have been saved successfully!")
        self.close()