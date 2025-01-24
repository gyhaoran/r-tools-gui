from core.window import SettingPageRegistor, SettingPageId
from ui.icons import M_TOOLS_PIN_RULE_ICON
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QInputDialog,
    QDoubleSpinBox,
    QWidget,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QFormLayout,
    QMessageBox,
    QSizePolicy,
    QListView,
)
from PyQt5.QtCore import pyqtSignal
import qtawesome as qta


class PinAssessRuleWidget(QWidget):
    rule_added = pyqtSignal(str)
    rule_deleted = pyqtSignal(str)
    rule_changed = pyqtSignal(bool)
    
    DEAFALUET_RULES = {
            "smic14": {"min_width": 0.020, "min_space": 0.020, "expand": True},
            "smic7" : {"min_width": 0.010, "min_space": 0.010, "expand": False},
            "asap7" : {"min_width": 0.018, "min_space": 0.018, "expand": True},
        }
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.is_modified = False
        self.pac_rules = settings.get("pac_rules", self.DEAFALUET_RULES)
        self._cur_rule = settings.get("pac", "smic14")
        self.init_ui(self._cur_rule)

    def init_ui(self, last_select):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self.setup_rule_selection(form_layout)
        self.setup_parameter_inputs(form_layout)
        self.setup_current_rule_label(layout)

        self.rule_combo.setCurrentText(last_select)
        self.update_rule_parameters()
        self.connect_signals()

    def setup_rule_selection(self, form_layout):
        rule_layout = QHBoxLayout()
        self.rule_combo = QComboBox()
        self.rule_combo.addItems(self.pac_rules.keys())
        self.rule_combo.setEditable(False)

        list_view = QListView(self)
        list_view.setStyleSheet(self.get_list_view_style())
        self.rule_combo.setView(list_view)
        
        self.rule_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rule_layout.addWidget(self.rule_combo)
        self.add_rule_button = self.create_button("fa.plus", self.add_rule)
        rule_layout.addWidget(self.add_rule_button)
        self.delete_rule_button = self.create_button("fa.trash-o", self.delete_rule)
        rule_layout.addWidget(self.delete_rule_button)
        form_layout.addRow("Rule:", rule_layout)

    def get_list_view_style(self):
        return """
            QListView::item {
                padding: 5px;
            }
            QListView {
                spacing: 5px;
            }
            QListView::indicator {
                width: 0px;
                height: 0px;
            }
            QListView::indicator {
                width: 0px;
                height: 0px;
            }
        """

    def create_button(self, icon_name, callback):
        button = QPushButton()
        button.setIcon(qta.icon(icon_name))
        button.setFixedSize(30, 30)
        button.clicked.connect(callback)
        return button

    def setup_parameter_inputs(self, form_layout):
        self.min_width_spinbox = self.create_spinbox(0.001, 10.0, 3, 0.01)
        form_layout.addRow("Minimum Width (µm):", self.min_width_spinbox)

        self.min_space_spinbox = self.create_spinbox(0.001, 10.0, 3, 0.01)
        form_layout.addRow("Minimum Spacing (µm):", self.min_space_spinbox)

        self.expand_checkbox = QCheckBox("Enable Pin Expand")
        form_layout.addRow(self.expand_checkbox)

    def create_spinbox(self, min_val, max_val, decimals, step):
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setDecimals(decimals)
        spinbox.setSingleStep(step)
        return spinbox

    def setup_current_rule_label(self, layout):
        self.current_rule_label = QLabel("Current Rule:  asap7")
        self.current_rule_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.current_rule_label.setFixedHeight(30)
        layout.addWidget(self.current_rule_label)

    def connect_signals(self):
        self.min_width_spinbox.valueChanged.connect(self.mark_as_modified)
        self.min_width_spinbox.textChanged.connect(self.mark_as_modified)
        self.min_space_spinbox.valueChanged.connect(self.mark_as_modified)
        self.min_space_spinbox.textChanged.connect(self.mark_as_modified)
        self.expand_checkbox.stateChanged.connect(self.mark_as_modified)

    def disconnect_signals(self):
        self.min_width_spinbox.valueChanged.disconnect(self.mark_as_modified)
        self.min_width_spinbox.textChanged.disconnect(self.mark_as_modified)
        self.min_space_spinbox.valueChanged.disconnect(self.mark_as_modified)
        self.min_space_spinbox.textChanged.disconnect(self.mark_as_modified)
        self.expand_checkbox.stateChanged.disconnect(self.mark_as_modified)        

    def has_modified(self)-> bool:
        return self.is_modified
    
    def mark_as_modified(self):
        if not self.is_modified:
            self.is_modified = True
            self.rule_changed.emit(True)

    def update_rule_parameters(self):
        rule_name = self.rule_combo.currentText()
        if rule_name in self.pac_rules:
            params = self.pac_rules[rule_name]
            self.min_width_spinbox.setValue(params["min_width"])
            self.min_space_spinbox.setValue(params["min_space"])
            self.expand_checkbox.setChecked(params["expand"])
        self.current_rule_label.setText(f"Current Rule:  {rule_name}")

    def _save_parameters(self):
        rule_name = self.rule_combo.currentText()
        if rule_name in self.pac_rules:
            params = self.pac_rules[rule_name]
            params["min_width"] = self.min_width_spinbox.value()
            params["min_space"] = self.min_space_spinbox.value()
            params["expand"] = self.expand_checkbox.isChecked()
            
    def save(self):
        self.is_modified = False
        self._save_parameters()

    def add_rule(self):
        new_rule_name, ok = QInputDialog.getText(self, "Add Rule", "Enter new rule name:")
        if ok and new_rule_name:
            if new_rule_name in self.pac_rules:
                QMessageBox.warning(self, "Error", "Rule name already exists!")
            else:
                self.disconnect_signals()
                self.rule_combo.addItem(new_rule_name)
                self.rule_combo.setCurrentText(new_rule_name)
                self.pac_rules[new_rule_name] = {"min_width": 0.1, "min_space": 0.1, "expand": False}
                self.rule_added.emit(new_rule_name)
                self.connect_signals()

    def delete_rule(self):
        rule_name = self.rule_combo.currentText()
        if len(self.pac_rules) <= 1:
            QMessageBox.warning(self, "Error", "At least one rule must remain!")
            return
        confirm = QMessageBox.question(
            self, "Delete Rule", f"Are you sure you want to delete rule '{rule_name}'?", QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.disconnect_signals()
            self.rule_combo.removeItem(self.rule_combo.currentIndex())
            del self.pac_rules[rule_name]
            self.update_rule_parameters()
            self.rule_deleted.emit(rule_name)
            self.connect_signals()

    def get_cur_setting(self):
        return self.rule_combo.currentText()
    
    def get_setting(self):
        settins = {"pac": self.get_cur_setting(), "pac_rules": self.pac_rules}
        return settins


class PinAssessRulePage(SettingPageRegistor):
    """Pac setting page"""
    def __init__(self, settings, parent=None):
        super().__init__(SettingPageId.PAC_SETTING_ID)    
        self._widget = PinAssessRuleWidget(settings, parent)
        
    def has_modified(self)-> bool:
        return self._widget.has_modified()
            
    def save(self):
        self._widget.save()

    def get_setting(self):
        return self._widget.get_setting()        

    def widget(self):
        return self._widget
        
    def title(self):
        return "PAC Rule"
    
    def icon(self):
        return M_TOOLS_PIN_RULE_ICON
    