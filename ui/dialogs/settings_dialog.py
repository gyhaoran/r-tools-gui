from .settingpages import *
from ui.icons import *
from core import setting_manager, SettingManager

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QMessageBox,
)
import qtawesome as qta


class SettingsDialog(QDialog):
    def __init__(self, parent=None, tab_index=0):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.general_tab = GeneralSettingsPage(self)
        self.tabs.addTab(self.general_tab, "General Settings")
        self.tabs.setTabIcon(0, qta.icon(M_TOOLS_SETTINGS_ICON))
        
        pac_rules = setting_manager().pac_rules
        drc_rules = setting_manager().drc_rules

        self.pin_rule_tab = PinAssessRulePage(pac_rules, setting_manager().pac, parent=self)
        self.tabs.addTab(self.pin_rule_tab, "PAC Rule")
        self.tabs.setTabIcon(1, qta.icon(M_TOOLS_PIN_RULE_ICON))
        self.pin_rule_tab.rule_added.connect(self.update_settings)
        self.pin_rule_tab.rule_deleted.connect(self.update_settings)
        self.pin_rule_tab.rule_changed.connect(lambda is_modified: self.update_tab_title(1, is_modified))
        
        self.drc_rule_tab = DrcRulePage(drc_rules, setting_manager().drc, parent=self)
        self.tabs.addTab(self.drc_rule_tab, "DRC Rule")
        self.tabs.setTabIcon(2, qta.icon(M_TOOLS_DRC_RULE_ICON))
        self.drc_rule_tab.rule_added.connect(self.update_settings)
        self.drc_rule_tab.rule_deleted.connect(self.update_settings)
        self.drc_rule_tab.rule_changed.connect(lambda is_modified: self.update_tab_title(2, is_modified))

        self.tabs.setCurrentIndex(tab_index)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.on_cancel)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
    def update_tab_title(self, tab_index, is_modified):
        """Update the tab title to indicate unsaved changes."""
        tab_text = self.tabs.tabText(tab_index)
        if is_modified and not tab_text.endswith(" *"):
            self.tabs.setTabText(tab_index, tab_text + " *")
        elif not is_modified and tab_text.endswith(" *"):
            self.tabs.setTabText(tab_index, tab_text.rstrip(" *"))

    def update_settings(self, rule_name=None):
        general_rule = self.general_tab.get_settings()
        pac_rule = self.pin_rule_tab.get_settings()
        drc_rule = self.drc_rule_tab.get_settings()
        setting_manager().update_cur_settings(general_rule, pac_rule, drc_rule)
        
        pac_rules = self.pin_rule_tab.export_pac_rules()
        drc_rules = self.drc_rule_tab.export_drc_rules()
        setting_manager().update_settings(pac_rules, drc_rules)
        
    def save_settings(self):
        """save settings"""
        self.update_settings()
        
        QMessageBox.information(self, "Saved", "Settings have been saved successfully!")

        for index in range(self.tabs.count()):
            self.update_tab_title(index, is_modified=False)
        
    def _is_modified(self):
        return self.pin_rule_tab.is_modified or self.drc_rule_tab.is_modified
    
    def on_cancel(self):
        """Handle the Cancel button click."""
        if self._is_modified():
            confirm = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to cancel?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.No:
                return  # User chose not to cancel
        self.reject()  # Close the dialog
        