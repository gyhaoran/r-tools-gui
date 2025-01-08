from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QSizePolicy,
    QPushButton,
    QFormLayout,
    QMessageBox,
    QInputDialog,
    QDoubleSpinBox,
    QListView,
)
from PyQt5.QtCore import pyqtSignal
import qtawesome as qta


class DrcRulePage(QWidget):
    rule_added = pyqtSignal(str)
    rule_deleted = pyqtSignal(str)
    rule_changed = pyqtSignal(bool)
    
    def __init__(self, rule_parameters, last_select, parent=None):
        super().__init__(parent)
        
        self.is_modified = False

        layout = QVBoxLayout(self)      
        
        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        rule_layout = QHBoxLayout()        
        self.rule_combo = QComboBox()
        self.rule_combo.addItems(rule_parameters.keys())  
        self.rule_combo.setEditable(False)
        self.rule_combo.currentIndexChanged.connect(self.update_rule_parameters)  

        list_view = QListView(self)
        list_view.setStyleSheet("""
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
        """)
        self.rule_combo.setView(list_view)
        
        # Set QComboBox to expand and fill available space
        self.rule_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        rule_layout.addWidget(self.rule_combo)

        # Add rule button (icon: +)
        self.add_rule_button = QPushButton()
        self.add_rule_button.setIcon(qta.icon("fa.plus"))
        self.add_rule_button.setFixedSize(30, 30)
        self.add_rule_button.clicked.connect(self.add_rule)
        rule_layout.addWidget(self.add_rule_button)

        # Delete rule button (icon: -)
        self.delete_rule_button = QPushButton()
        self.delete_rule_button.setIcon(qta.icon("fa.trash-o")) 
        self.delete_rule_button.setFixedSize(30, 30) 
        self.delete_rule_button.clicked.connect(self.delete_rule)
        rule_layout.addWidget(self.delete_rule_button)

        form_layout.addRow("Rule:", rule_layout)

        # Minimum width setting
        self.min_width_spinbox = QDoubleSpinBox()
        self.min_width_spinbox.setRange(0.001, 10.0)  
        self.min_width_spinbox.setDecimals(3) 
        self.min_width_spinbox.setSingleStep(0.01)
        form_layout.addRow("Minimum Width (µm):", self.min_width_spinbox)

        # Minimum spacing setting
        self.min_space_spinbox = QDoubleSpinBox()
        self.min_space_spinbox.setRange(0.001, 10.0)
        self.min_space_spinbox.setDecimals(3)
        self.min_space_spinbox.setSingleStep(0.01)
        form_layout.addRow("Minimum Spacing (µm):", self.min_space_spinbox)

        # Minimum contact size setting
        self.min_contact_size_spinbox = QDoubleSpinBox()
        self.min_contact_size_spinbox.setRange(0.001, 10.0)  
        self.min_contact_size_spinbox.setValue(0.2)  
        self.min_contact_size_spinbox.setSingleStep(0.001)
        form_layout.addRow("Minimum Contact Size (µm):", self.min_contact_size_spinbox)

        self.current_rule_label = QLabel("Current Rule:  asap7")
        self.current_rule_label.setStyleSheet("font-size: 15px; font-weight: bold;") 
        self.current_rule_label.setFixedHeight(30)
        layout.addWidget(self.current_rule_label)

        # Dictionary to store rule parameters
        self.rule_parameters = rule_parameters

        # Initialize UI with the first rule's parameters
        self.rule_combo.setCurrentText(last_select)
        self.update_rule_parameters()

        self.min_width_spinbox.valueChanged.connect(self.mark_as_modified)
        self.min_space_spinbox.valueChanged.connect(self.mark_as_modified)
        self.min_contact_size_spinbox.valueChanged.connect(self.mark_as_modified)        
        
    def mark_as_modified(self):
        """Mark rule changed"""
        if not self.is_modified:
            self.is_modified = True
            self.rule_changed.emit(True)
                    
    def update_rule_parameters(self):
        """Update UI with the selected rule's parameters."""
        rule_name = self.rule_combo.currentText()
        if rule_name in self.rule_parameters:
            params = self.rule_parameters[rule_name]
            self.min_width_spinbox.setValue(params["min_width"])
            self.min_space_spinbox.setValue(params["min_space"])
            self.min_contact_size_spinbox.setValue(params["min_contact_size"])
        self.current_rule_label.setText(f"Current Rule:  {rule_name}")

    def _save_parameters(self):
        rule_name = self.rule_combo.currentText()
        if rule_name in self.rule_parameters:
            params = self.rule_parameters[rule_name]
            params["min_width"] = self.min_width_spinbox.value()
            params["min_space"] = self.min_space_spinbox.value()
            params["min_contact_size"] = self.min_contact_size_spinbox.value()
            
    def save(self):
        """Save user modify"""
        self.is_modified = False
        self._save_parameters()
                
    def add_rule(self):
        """Add a new rule."""
        new_rule_name, ok = QInputDialog.getText(self, "Add Rule", "Enter new rule name:")
        if ok and new_rule_name:
            if new_rule_name in self.rule_parameters:
                QMessageBox.warning(self, "Error", "Rule name already exists!")
            else:
                self.rule_combo.addItem(new_rule_name)
                self.rule_combo.setCurrentText(new_rule_name)
                self.rule_parameters[new_rule_name] = {"min_width": 0.1, "min_space": 0.1, "min_contact_size": 0.2}
                self.rule_added.emit(new_rule_name)

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
            self.rule_deleted.emit(rule_name)

    def get_settings(self):
        """Get the current rule's settings."""
        return self.rule_combo.currentText()
        
    def export_drc_rules(self):
        """Export all rules as a dictionary."""
        return self.rule_parameters
