from .settingpages import *
from core.window.setting_page_id import SettingPageId

from core import setting_manager, SettingManager
from core.window import setting_page_manager, SettingPageManager
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import pyqtSignal
import qtawesome as qta


class SettingsDialog(QDialog):
    save_setting_signal = pyqtSignal()
    
    def __init__(self, parent=None, tab_index=0):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 400)

        self.main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self._create_setting_page()
        self.setup_tabs(tab_index)
        self.setup_buttons()
        
    def _create_setting_page(self):
        general_tab = GeneralSettingsPage(self)
        pin_rule_tab = PinAssessRulePage(setting_manager()._all_settings, self)
        drc_rule_tab = DrcRulePage(setting_manager()._all_settings, self)
        
        setting_manager().add_pages({SettingPageId.GENERAL_SETTING_ID: general_tab, 
                                     SettingPageId.PAC_SETTING_ID: pin_rule_tab, 
                                     SettingPageId.DRC_SETTING_ID: drc_rule_tab})

    def setup_tabs(self, tab_index):
        """Initialize and add tabs to the dialog."""
        for i, (_, page) in enumerate(setting_manager().get_pages().items()):
            self.add_tab(page, page.title(), page.icon())
            self.connect_rule_signals(page, i)
        self.tabs.setCurrentIndex(tab_index)

    def add_tab(self, widget, title, icon):
        """Add a tab with the given widget, title, and icon."""
        self.tabs.addTab(widget, title)
        self.tabs.setTabIcon(self.tabs.count() - 1, qta.icon(icon))

    def connect_rule_signals(self, page, tab_index):
        """Connect signals for rule tabs."""
        if not all(hasattr(page, obj) for obj in ['rule_added', 'rule_deleted', 'rule_changed']):
            return        
        # page.rule_added.connect(self.update_settings)
        # page.rule_deleted.connect(self.update_settings)
        page.rule_changed.connect(lambda is_modified: self.update_tab_title(tab_index, is_modified))

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

    def update_settings(self):
        """Update settings in the setting manager."""
        setting_manager().update_settings()

    def save_settings(self):
        """Save settings and update the UI."""
        setting_manager().save()
        self.update_settings()
        for index in range(self.tabs.count()):
            self.update_tab_title(index, is_modified=False)

    @property
    def _is_modified(self):
        """Check if any tab has unsaved changes."""
        return setting_manager().has_modified()

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
            