import sys 
import json
from collections import deque
from PyQt5.QtWidgets import (QWidget, QTabWidget, QFormLayout, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem,
                             QToolBar, QAction, QTreeWidget, QTreeWidgetItem, QInputDialog, QTableWidget, QHeaderView, QMessageBox, QMenu,
                             QComboBox, QLineEdit, QPushButton, QListWidget, QDialog, QDialogButtonBox, QMainWindow, QApplication, QCheckBox)
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
from PyQt5.QtGui import QIntValidator, QRegExpValidator
 

# =================================================== 
# Integrated Configuration Dialog with Tabs 
# =================================================== 
class AprConfigDialog(QDialog):
    """Integrated configuration dialog with Place/Route tabs"""
    def __init__(self, max_row=5):
        super().__init__()
        self.setWindowTitle("Place&Route Config")
        self._init_ui(max_row)
        self.has_params_changed = False
    
    def update_tab_title(self, index, is_modified):
        """Update tab title to indicate unsaved changes"""
        tab_text = self.tab_widget.tabText(index)
        if is_modified and not tab_text.endswith(" *"):
            self.tab_widget.setTabText(index, tab_text + " *")
        elif not is_modified and tab_text.endswith(" *"):
            self.tab_widget.setTabText(index, tab_text[:-2])
        self.has_params_changed = any([self.place_tab.params_changed, self.route_tab.params_changed])
    
    def _connect_signals(self):
        """Connect signals to parameter changes"""
        self.place_tab.params_changed.connect(lambda is_modified: self.update_tab_title(0, is_modified))
        self.route_tab.params_changed.connect(lambda is_modified: self.update_tab_title(1, is_modified))
 
    def _init_ui(self, max_row):
        self.tab_widget = QTabWidget()
        
        self.place_tab  = PlaceConfigTab()
        self.route_tab  = RouteConfigTab(max_row)
        
        self.tab_widget.addTab(self.place_tab, "Place")
        self.tab_widget.addTab(self.route_tab, "Route")
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept) 
        btn_box.rejected.connect(self.reject) 
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget) 
        main_layout.addWidget(btn_box) 
        self.setLayout(main_layout)

        
    def accept(self):
        """Validate configuration before closing dialog"""
        if self.has_params_changed:
            reply = QMessageBox.question(self, "Unsaved Changes", "Save changes before closing?", QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
            if reply == QMessageBox.Save:
                self.save_settings()
            elif reply == QMessageBox.Cancel:
                self.reject()
        else:
            super().accept()
    
    def save_settings(self):
        """Save configuration changes"""
        print("Saving configuration changes...")
        self.update_tab_title(0, False)
        self.update_tab_title(1, False)
    
    def get_config(self):
        """Combine configurations from both tabs"""
        return dict([
            ("place", self.place_tab.get_config()), 
            ("route", self.route_tab.get_config()) 
        ])
 
# =================================================== 
# Place Configuration Tab 
# =================================================== 
class PlaceConfigTab(QWidget):
    """Placement configuration tab content"""
    params_changed = pyqtSignal(bool) # Signal for parameter changes
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect signals to parameter changes"""
        self.placer_combo.currentIndexChanged.connect(self._emit_signal)
        self.num_candidates.valueChanged.connect(self._emit_signal)
        self.num_results.valueChanged.connect(self._emit_signal)
        self.optimize_combo.currentIndexChanged.connect(self._emit_signal)
    
    def _emit_signal(self):
        """Emit signal for parameter changes"""
        self.params_changed.emit(True)
    
    def _init_ui(self):
        self.placer_combo  = QComboBox(self)
        self.placer_combo.addItems(["hueristic_euler_placer"])
        
        self.num_candidates  = self._create_spinbox(1, 300, 300)
        self.num_results = self._create_spinbox(1, 5, 1)
        self.num_candidates.valueChanged.connect(lambda v: self.num_results.setMaximum(v)) 
        
        self.optimize_combo  = QComboBox(self)
        self.optimize_combo.addItems(["Default",  "Congestion", "WireLength", "MH-AlignPoly"])
         
        form = QFormLayout()
        form.addRow(self._form_row("Placer:", self.placer_combo)) 
        form.addRow(self._form_row("Number of Candidates:", self.num_candidates)) 
        form.addRow(self._form_row("Number of Results:", self.num_results)) 
        form.addRow(self._form_row("Optimization Strategy:", self.optimize_combo))
        self.setLayout(form) 

    def _form_row(self, label_text, widget):
        """Generate aligned form row with dynamic spacing"""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)        
        label = QLabel(label_text)
        
        row.addWidget(label, stretch=1) 
        row.addWidget(widget, stretch=1)
        
        return row  
        
    def _create_spinbox(self, min_val, max_val, default):      
        spin = QSpinBox(self)
        spin.setRange(min_val, max_val)
        spin.setValue(default) 
        return spin 
    
    def get_config(self):
        """Export placement config"""
        return dict([
            ("placer", self.placer_combo.currentText()), 
            ("num_candidates", self.num_candidates.value()), 
            ("num_results", self.num_results.value()), 
            ("optimize", self.optimize_combo.currentText()) 
        ])

# ===================================================
# Enhanced Route Configuration Tab 
# ===================================================
class RouteConfigTab(QWidget):
    """Main container for routing configuration with tabbed interface"""
    params_changed = pyqtSignal(bool) # Signal for parameter changes
    
    def __init__(self, max_row):
        super().__init__()
        self._init_ui(max_row)
        self._connect_signals()
        
    def _connect_signals(self):
        """Connect signals to parameter changes"""
        self.router_combo.currentIndexChanged.connect(self._emit_signal)
        self.num_results.valueChanged.connect(self._emit_signal)
        self.output_multi_pins.stateChanged.connect(self._emit_signal)
        self.max_poly_check.stateChanged.connect(self._emit_signal)
        self.via_editor.params_changed.connect(self._emit_signal)
        self.pin_editor.params_changed.connect(self._emit_signal)
        self.forbidden_editor.params_changed.connect(self._emit_signal)
        
    def _emit_signal(self):
        """Emit signal for parameter changes"""
        self.params_changed.emit(True)
    
    def _init_ui(self, max_row):
        # Initialize tab container 
        tab_widget = QTabWidget()
        
        basic_tab = self._create_basic_tab()
        self.via_editor = ViaCostMatrix(max_row)
        self.pin_editor = PinLocationEditor()
        self.forbidden_editor  = ForbiddenTrackManager()
        
        tab_widget.addTab(basic_tab, "Basic")
        tab_widget.addTab(self.via_editor, "Via Cost")
        tab_widget.addTab(self.pin_editor, "Pin Locations")
        tab_widget.addTab(self.forbidden_editor, "Forbidden Tracks")        
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget) 
        self.setLayout(main_layout)
        
    def _create_basic_tab(self):
        """Initialize basic configuration panel"""
        container = QWidget()
        form = QFormLayout()
        
        # Router type selector 
        self.router_combo = QComboBox(self)
        self.router_combo.addItems(["ilp_router"])
        
        self.num_results = QSpinBox(self)
        self.num_results.setRange(1,  10)
        self.num_results.setValue(3) 
        
        self.output_multi_pins = QCheckBox(self)
        self.max_poly_check = QCheckBox(self)
        
        # Add aligned form rows 
        form.addRow(self._form_row("Routing Algorithm:", self.router_combo)) 
        form.addRow(self._form_row("Maximum Results:", self.num_results)) 
        form.addRow(self._form_row("Multi-pin Output:", self.output_multi_pins)) 
        form.addRow(self._form_row("Limit Polygon Length:", self.max_poly_check)) 
        
        container.setLayout(form) 
        return container 
    
    def _form_row(self, label_text, widget):
        """Generate aligned form row with dynamic spacing"""
        container = QWidget(self)
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text, container)        
        row.addWidget(label, stretch=1) 
        row.addWidget(widget, stretch=1)        
        return container 
    
    def get_config(self):
        """Export configuration data with validation"""
        return dict([
            ("algorithm", self.router_combo.currentText()), 
            ("max_results", self.num_results.value()), 
            ("multi_pin_output", self.output_multi_pins.isChecked()), 
            ("polygon_length_limit", self.max_poly_check.isChecked()), 
            ("rules", dict([
                ("via_costs", self.via_editor.get_data()), 
                ("pin_locations", self.pin_editor.get_data()), 
                ("restricted_tracks", self.forbidden_editor.get_data()) 
            ]))
        ])
 
class ViaCostMatrix(QWidget):
    """Dynamic via cost matrix with layer-oriented configuration"""
    
    def __init__(self, max_row=5):
        super().__init__()
        self.via_defs = list(["V0", "V1", "V2", "V3"])
        self.max_row = max_row
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI with reversed table structure"""
        layout = QVBoxLayout()
        
        # Configure table with dynamic columns 
        self.table = QTableWidget(0, self.max_row + 1) 
        headers = ["Layer"] + [str(i) for i in range(self.max_row)]
        self.table.setHorizontalHeaderLabels(headers) 
        self.table.verticalHeader().setVisible(False) 
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, Qt.AscendingOrder)
        
        # Add control buttons 
        self.add_btn = QPushButton("Add Via Layer")
        self.add_btn.clicked.connect(self._add_layer_row) 
        
        layout.addWidget(self.table) 
        layout.addWidget(self.add_btn) 
        self.setLayout(layout)
    
    def _show_context_menu(self, pos):
        """Show context menu for layer deletion"""
        row = self.table.indexAt(pos).row()
        if row >= 0:
            menu = QMenu()
            delete_action = menu.addAction("Delete Layer")
            action = menu.exec_(self.table.viewport().mapToGlobal(pos))
            if action == delete_action:
                self.via_defs.appendleft(self.table.item(row, 0).text())
                self.table.removeRow(row)
    
    def _add_layer_row(self):
        """Insert new layer row with default configuration"""
        if not self.via_defs:
            QMessageBox.warning(self, "Warning", "No more via layers available!")
            return
        row = self.table.rowCount() 
        self.table.insertRow(row) 
        
        layer_name = self.via_defs.popleft()
        layer_item = QTableWidgetItem(layer_name)
        layer_item.setFlags(Qt.ItemIsEnabled)   # Make non-editable 
        self.table.setItem(row, 0, layer_item)
        
        # Add cost spinboxes for each row 
        for col in range(1, self.max_row + 1):
            input = QLineEdit()
            input.setText("-") 
            input.setAlignment(Qt.AlignCenter) 
            self.table.setCellWidget(row, col, input)
    
    def get_data(self):
        """Export configuration in structured format"""
        config = dict()
        for row in range(self.table.rowCount()): 
            layer = self.table.item(row,  0).text()
            config[layer] = {}
            for col in range(1, 6):
                row_id = str(col-1)  # Convert column to 0-4 
                spinbox = self.table.cellWidget(row,  col)
                if spinbox.text().isdigit():
                    config[layer][row_id] = spinbox.text() 
        return config 
    
class PinLocationEditor(QWidget):
    """Grid-based editor for pin location configuration"""
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Table configuration 
        self.table  = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Pin", "Layer", "Track", "Start", "End"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
                
        # Control buttons 
        add_btn = QPushButton("Add Pin Location")
        add_btn.clicked.connect(self._add_pin_row) 
        
        layout.addWidget(self.table) 
        layout.addWidget(add_btn) 
        self.setLayout(layout) 

    def _show_context_menu(self, pos):
        """Show context menu for pin deletion"""
        row = self.table.indexAt(pos).row()
        if row >= 0:
            menu = QMenu()
            delete_action = menu.addAction("Delete Pin")
            action = menu.exec_(self.table.viewport().mapToGlobal(pos))
            if action == delete_action:
                self.table.removeRow(row)
    
    def _add_pin_row(self):
        """Insert new pin configuration row"""
        row = self.table.rowCount() 
        self.table.insertRow(row) 
        
        pin_name = QTableWidgetItem("Pin Name")
        # pin_name.setFlags(Qt.ItemIsEnabled)   # Make non-editable 
        self.table.setItem(row, 0, pin_name)
        
        layer_combo = QComboBox()
        layer_combo.addItems([f"M{i}"  for i in range(1, 4)])       
        self.table.setCellWidget(row,  1, layer_combo)
        for col in [2,3,4]:
            spin = QSpinBox()
            spin.setRange(0, 9999)
            self.table.setCellWidget(row, col, spin)
    
    def get_data(self):
        """Generate structured pin location data"""
        pins = dict()
        for idx in range(self.table.rowCount()): 
            try:
                pin_id = self.table.item(idx, 0).text()
                layer = self.table.cellWidget(idx, 1).currentText()
                track = self.table.cellWidget(idx, 2).value()
                start = self.table.cellWidget(idx, 3).value()
                end = self.table.cellWidget(idx, 4).value()                
                pins[pin_id] = {"layer": layer, "track": track, "start": start, "end": end}
            except:
                continue
        return pins 
 
class ForbiddenTrackManager(QWidget):
    """Interactive manager for restricted track configurations"""
    def __init__(self):
        super().__init__()
        self.max_layers = 3
        self.layers_def = deque([f"M{i}" for i in range(1, self.max_layers + 1)])
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        self.table  = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Layer", "Forbidden Tracks", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 40)
        
        # Control buttons 
        add_btn = QPushButton("Add Pin Location")
        add_btn.clicked.connect(self._add_forbidden_row) 
        
        layout.addWidget(self.table) 
        layout.addWidget(add_btn) 
        self.setLayout(layout)         

    def _show_context_menu(self, pos):
        """Show context menu for layer deletion"""
        row = self.table.indexAt(pos).row()
        if row >= 0:
            menu = QMenu()
            delete_action = menu.addAction("Delete Layer")
            action = menu.exec_(self.table.viewport().mapToGlobal(pos))
            if action == delete_action:
                self._delete_row(row)

    
    def _add_forbidden_row(self):
        if not self.layers_def:
            QMessageBox.warning(self, "Warning", "No more layers available!")
            return
        row = self.table.rowCount() 
        self.table.insertRow(row) 
        
        layer_name = self.layers_def.popleft()
        layer_item = QTableWidgetItem(layer_name)
        layer_item.setFlags(Qt.ItemIsEnabled)   # Make non-editable 
        self.table.setItem(row, 0, layer_item)
        
        forbid_tracks = QLineEdit()
        forbid_tracks.setPlaceholderText("track: (e.g., 1-5,8,10)")
        pattern = r'^(\d+(-\d+)?)(,\s*\d+(-\d+)?)*$'  # match numbers or ranges, e.g. 1-3,5,7-9 
        forbid_tracks.setValidator(QRegExpValidator(QRegExp(pattern))) 
        forbid_tracks.editingFinished.connect(lambda : self._validate_track_input(forbid_tracks)) 
        self.table.setCellWidget(row, 1, forbid_tracks)        
        self._create_delete_button(row)
    
    def _delete_row(self, row):
        self.layers_def.appendleft(self.table.item(row, 0).text())
        self.table.removeRow(row)
    
    def _create_delete_button(self, row):
        import qtawesome as qta
        delete_btn = QPushButton(qta.icon("fa.trash"), "")
        delete_btn.clicked.connect(lambda: self._delete_row(row))
        self.table.setCellWidget(row, 2, delete_btn)
    
    def _validate_track_input(self, forbid_tracks):
        input_text = forbid_tracks.text()
        if not self._is_valid_track_format(input_text):
            forbid_tracks.setStyleSheet("border:  1px solid red;")
            QMessageBox.warning(self,  "Format Error", "Invalid format! Correct examples:\n1-5,8,10 or 3,7-9")
            forbid_tracks.setText("")
        else:
            forbid_tracks.setStyleSheet("")
            
    def _is_valid_track_format(self, input_text):
        """Validate track range format (e.g. '1-5,8,10')"""
        if not input_text:
            return True 
        
        segments = input_text.replace("  ", "").split(',')
        for seg in segments:
            if '-' in seg:
                parts = seg.split('-') 
                if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                    return False 
                if int(parts[0]) > int(parts[1]):
                    return False 
            else:
                if not seg.isdigit(): 
                    return False 
        return True

    def _process_input(self, input_text):
        """Convert valid input string to sorted integer list"""
        tracks = []
        if not input_text:
            return tracks 
        
        for seg in input_text.replace("  ", "").split(','):
            if '-' in seg:
                start, end = sorted(map(int, seg.split('-'))) 
                tracks.extend(range(start,  end + 1))
            else:
                tracks.append(int(seg)) 
        
        return sorted(list(set(tracks))) 

    def get_data(self):
        """Export restricted track configuration"""
        forbidden_tracks = dict()
        for idx in range(self.table.rowCount()): 
            try:
                layer = self.table.item(idx, 0).text()
                tracks = self._process_input(self.table.cellWidget(idx, 1).text())
                forbidden_tracks[layer] = tracks
            except:
                continue
        return forbidden_tracks
 
# =================================================== 
# Main Window with Testing Interface 
# =================================================== 
class MainWindow(QMainWindow):
    """Main application window with toolbar"""
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("EDA  Configuration Tool")
        self.setGeometry(100,  100, 800, 600)
        
        # Create toolbar 
        toolbar = self.addToolBar("Actions") 
        config_act = QAction("Show Config", self)
        toolbar.addAction(config_act) 
        config_act.triggered.connect(self.show_config_dialog) 
    
    def show_config_dialog(self):
        dialog = AprConfigDialog()
        dialog.exec_()
            
 
# =================================================== 
# Application Entry Point 
# =================================================== 
if __name__ == "__main__":
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_()) 
