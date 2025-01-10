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

        self.main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self.setup_tabs(tab_index)
        self.setup_buttons()

    def setup_tabs(self, tab_index):
        """Initialize and add tabs to the dialog."""
        self.general_tab = GeneralSettingsPage(self)
        self.add_tab(self.general_tab, "General Settings", M_TOOLS_SETTINGS_ICON)

        pac_rules = setting_manager().pac_rules
        drc_rules = setting_manager().drc_rules

        self.pin_rule_tab = PinAssessRulePage(pac_rules, setting_manager().pac, parent=self)
        self.add_tab(self.pin_rule_tab, "PAC Rule", M_TOOLS_PIN_RULE_ICON)
        self.connect_rule_signals(self.pin_rule_tab, 1)

        self.drc_rule_tab = DrcRulePage(drc_rules, setting_manager().drc, parent=self)
        self.add_tab(self.drc_rule_tab, "DRC Rule", M_TOOLS_DRC_RULE_ICON)
        self.connect_rule_signals(self.drc_rule_tab, 2)

        self.tabs.setCurrentIndex(tab_index)

    def add_tab(self, widget, title, icon):
        """Add a tab with the given widget, title, and icon."""
        self.tabs.addTab(widget, title)
        self.tabs.setTabIcon(self.tabs.count() - 1, qta.icon(icon))

    def connect_rule_signals(self, rule_tab, tab_index):
        """Connect signals for rule tabs."""
        rule_tab.rule_added.connect(self.update_settings)
        rule_tab.rule_deleted.connect(self.update_settings)
        rule_tab.rule_changed.connect(lambda is_modified: self.update_tab_title(tab_index, is_modified))

    def setup_buttons(self):
        """Initialize and add buttons to the dialog."""
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.on_cancel)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        self.main_layout.addLayout(button_layout)

    def update_tab_title(self, tab_index, is_modified):
        """Update the tab title to indicate unsaved changes."""
        tab_text = self.tabs.tabText(tab_index)
        if is_modified and not tab_text.endswith(" *"):
            self.tabs.setTabText(tab_index, tab_text + " *")
        elif not is_modified and tab_text.endswith(" *"):
            self.tabs.setTabText(tab_index, tab_text.rstrip(" *"))

    def update_settings(self, rule_name=None):
        """Update settings in the setting manager."""
        general_rule = self.general_tab.get_settings()
        pac_rule = self.pin_rule_tab.get_settings()
        drc_rule = self.drc_rule_tab.get_settings()
        setting_manager().update_cur_settings(general_rule, pac_rule, drc_rule)

        pac_rules = self.pin_rule_tab.export_pac_rules()
        drc_rules = self.drc_rule_tab.export_drc_rules()
        setting_manager().update_settings(pac_rules, drc_rules)

    def save_settings(self):
        """Save settings and update the UI."""
        self.pin_rule_tab.save()
        self.drc_rule_tab.save()
        self.update_settings()

        for index in range(self.tabs.count()):
            self.update_tab_title(index, is_modified=False)

    @property
    def _is_modified(self):
        """Check if any tab has unsaved changes."""
        return self.pin_rule_tab.is_modified or self.drc_rule_tab.is_modified

    def on_cancel(self):
        """Handle the Cancel button click."""
        if self._is_modified:
            confirm = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to cancel?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.No:
                return  # User chose not to cancel
        self.reject()  # Close the dialog

    def closeEvent(self, event):
        """Override closeEvent to handle unsaved changes."""
        if self._is_modified:
            confirm = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if confirm == QMessageBox.Save:
                self.save_settings()  # Save changes and close
                event.accept()
            elif confirm == QMessageBox.Discard:
                event.accept()  # Discard changes and close
            else:
                event.ignore()  # Cancel the close operation
        else:
            event.accept()  # No unsaved changes, close the dialog
            