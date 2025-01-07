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
    QSizePolicy
)
import qtawesome as qta


class PinAssessRulePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)      
        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        rule_layout = QHBoxLayout()

        self.rule_combo = QComboBox()
        self.rule_combo.addItems(["asap7", "smic-7", "smic-14"])  # Default rules
        self.rule_combo.setEditable(True)  # Allow user to edit rule names
        self.rule_combo.editTextChanged.connect(self.update_rule_parameters)
        self.rule_combo.currentIndexChanged.connect(self.update_rule_parameters)  # Update parameters when rule changes

        # Set QComboBox to expand and fill available space
        self.rule_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rule_layout.addWidget(self.rule_combo)

        # Add rule button (icon: +)
        self.add_rule_button = QPushButton()
        self.add_rule_button.setIcon(qta.icon("fa5s.plus")) 
        self.add_rule_button.setFixedSize(30, 30)
        self.add_rule_button.clicked.connect(self.add_rule)
        rule_layout.addWidget(self.add_rule_button)

        # Delete rule button (icon: -)
        self.delete_rule_button = QPushButton()
        self.delete_rule_button.setIcon(qta.icon("fa5s.minus")) 
        self.delete_rule_button.setFixedSize(30, 30)
        self.delete_rule_button.clicked.connect(self.delete_rule)
        rule_layout.addWidget(self.delete_rule_button)

        form_layout.addRow("Rule:", rule_layout)

        # Minimum width setting
        self.min_width_spinbox = QDoubleSpinBox()
        self.min_width_spinbox.setRange(0.01, 10.0)
        self.min_width_spinbox.setValue(0.1) 
        self.min_width_spinbox.setSingleStep(0.01) 
        form_layout.addRow("Minimum Width (µm):", self.min_width_spinbox)

        # Minimum spacing setting
        self.min_spacing_spinbox = QDoubleSpinBox()
        self.min_spacing_spinbox.setRange(0.01, 10.0)
        self.min_spacing_spinbox.setValue(0.1) 
        self.min_spacing_spinbox.setSingleStep(0.01) 
        form_layout.addRow("Minimum Spacing (µm):", self.min_spacing_spinbox)

        # Enable/disable Pin Expand feature
        self.enable_pin_expand_checkbox = QCheckBox("Enable Pin Expand")
        form_layout.addRow(self.enable_pin_expand_checkbox)

        # Add a stretchable spacer to separate the form layout and the current rule label
        layout.addStretch()

        # Current rule label (fixed height and more prominent)
        self.current_rule_label = QLabel("Current Rule:  asap7")
        self.current_rule_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.current_rule_label.setFixedHeight(30)
        layout.addWidget(self.current_rule_label)

        # Dictionary to store rule parameters
        self.rule_parameters = {
            "asap7": {"min_width": 0.6, "min_spacing": 0.6, "enable_pin_expand": True},
            "smic-7": {"min_width": 0.2, "min_spacing": 0.2, "enable_pin_expand": False},
            "smic-14": {"min_width": 0.3, "min_spacing": 0.3, "enable_pin_expand": True},
        }

        # Initialize UI with the first rule's parameters
        self.update_rule_parameters()

    def update_rule_parameters(self):
        """Update UI with the selected rule's parameters."""
        rule_name = self.rule_combo.currentText()
        if rule_name in self.rule_parameters:
            params = self.rule_parameters[rule_name]
            self.min_width_spinbox.setValue(params["min_width"])
            self.min_spacing_spinbox.setValue(params["min_spacing"])
            self.enable_pin_expand_checkbox.setChecked(params["enable_pin_expand"])
        self.current_rule_label.setText(f"Current Rule:  {rule_name}")

    def add_rule(self):
        """Add a new rule."""
        new_rule_name, ok = QInputDialog.getText(self, "Add Rule", "Enter new rule name:")
        if ok and new_rule_name:
            if new_rule_name in self.rule_parameters:
                QMessageBox.warning(self, "Error", "Rule name already exists!")
            else:
                self.rule_combo.addItem(new_rule_name)
                self.rule_combo.setCurrentText(new_rule_name)
                self.rule_parameters[new_rule_name] = {"min_width": 0.1, "min_spacing": 0.1, "enable_pin_expand": False}

    def delete_rule(self):
        """Delete the selected rule."""
        rule_name = self.rule_combo.currentText()
        if len(self.rule_parameters) <= 1:
            QMessageBox.warning(self, "Error", "At least one rule must remain!")
            return
        confirm = QMessageBox.question(
            self, "Delete Rule", f"Are you sure you want to delete rule '{rule_name}'?", QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.rule_combo.removeItem(self.rule_combo.currentIndex())
            del self.rule_parameters[rule_name]
            self.update_rule_parameters()

    def get_settings(self):
        """Get the current rule's settings."""
        rule_name = self.rule_combo.currentText()
        return {
            "rule_name": rule_name,
            "min_width": self.min_width_spinbox.value(),
            "min_spacing": self.min_spacing_spinbox.value(),
            "enable_pin_expand": self.enable_pin_expand_checkbox.isChecked(),
        }
        