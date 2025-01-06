import sys, os
import json
import qtawesome as qta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFileDialog, QDialog, QLabel, QFrame,
                             QHBoxLayout, QSpacerItem, QSizePolicy, QDesktopWidget, QMessageBox)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

class NewProjectDialog(QDialog):       
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("New Project")
        self.setGeometry(0, 0, 600, 450)
        self.move_to_center()
        
        title_label = QLabel("Create New Project", self)
        title_label.setFixedHeight(50)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        # Layouts
        self.main_layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.project_name = QLineEdit(self)
        self.project_name.setPlaceholderText("Input Project Name")
        self.project_name.setText("New_Project")
        self.project_name.setFixedWidth(200)  # Set a fixed width for the input field
        self.form_layout.addRow("Project Name:", self.project_name)
        self.project_name.textChanged.connect(self.update_create_button_state)

        self.location_input = QLineEdit(self)
        self.location_input.setPlaceholderText('Select Project Path')
        self.location_input.setText(os.path.expanduser('~'))
        self.browse_location_btn = QPushButton(self)
        self.browse_location_btn.setIcon(qta.icon('fa.folder-o'))  # Set an icon for folder
        self.browse_location_btn.clicked.connect(self.browse_location)
        location_layout = QHBoxLayout()
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(self.browse_location_btn)
        self.form_layout.addRow("Location:", location_layout)

        # Tech File
        self.tech_file_input = QLineEdit(self)
        self.tech_file_input.setPlaceholderText("Select Tech File")
        self.tech_file_input.textChanged.connect(self.update_create_button_state)
        self.browse_tech_btn = QPushButton(self)
        self.browse_tech_btn.setIcon(qta.icon('fa.folder-o'))  # Set an icon for tech file
        self.browse_tech_btn.clicked.connect(self.browse_tech_file)
        tech_layout = QHBoxLayout()
        tech_layout.addWidget(self.tech_file_input)
        tech_layout.addWidget(self.browse_tech_btn)
        self.form_layout.addRow("Tech File:", tech_layout)

        # Netlist File
        self.netlist_file_input = QLineEdit(self)
        self.netlist_file_input.setPlaceholderText("Select Netlist File")
        self.netlist_file_input.textChanged.connect(self.update_create_button_state)
        self.browse_netlist_btn = QPushButton(self)
        self.browse_netlist_btn.setIcon(qta.icon('fa.folder-o'))  # Set an icon for netlist file
        self.browse_netlist_btn.clicked.connect(self.browse_netlist_file)
        netlist_layout = QHBoxLayout()
        netlist_layout.addWidget(self.netlist_file_input)
        netlist_layout.addWidget(self.browse_netlist_btn)
        self.form_layout.addRow("Netlist File:", netlist_layout)

        # Create Button
        self.create_btn = QPushButton("Create", self)
        self.create_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                color: white;
            }
            QPushButton:enabled {
                background-color: #4CAF50; /* Green background when enabled */
            }
            QPushButton:disabled {
                background-color: #D3D3D3;     /* Gray background when disabled */
            }
        """)
        self.create_btn.clicked.connect(self.create_project)

        # Custom status bar layout
        status_bar_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        status_bar_layout.addItem(spacer)  # Spacer to push Create button to the right
        status_bar_layout.addWidget(self.create_btn)  # Add Create button

        # Add the custom status bar layout to the main layout
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(separator)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(status_bar_layout)

        self.setLayout(self.main_layout)
        
        self.update_create_button_state()

    def move_to_center(self):
        screen = QDesktopWidget().screenGeometry()  
        window_size = self.geometry()  
        x = (screen.width() - window_size.width()) // 2  
        y = (screen.height() - window_size.height()) // 2  
        self.move(x, y)
        
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Location")
        if folder:
            self.location_input.setText(folder)
            self.update_create_button_state()            

    def browse_tech_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Tech File", "", "Tech Files (*.tech);;All Files (*)")
        if file:
            self.tech_file_input.setText(file)
            self.update_create_button_state()            

    def browse_netlist_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Netlist File", "", "Netlist Files (*.sp *.spi);;All Files (*)")
        if file:
            self.netlist_file_input.setText(file)
            self.update_create_button_state()
            
    def update_create_button_state(self):
        """Enable the create button only if all inputs are non-empty."""
        all_fields_filled = bool(self.project_name.text()) and \
                            bool(self.location_input.text()) and \
                            bool(self.tech_file_input.text()) and \
                            bool(self.netlist_file_input.text())
        self.create_btn.setEnabled(all_fields_filled)

    def create_project(self):
        # Implement the create project logic
        project_name = self.project_name.text()
        location = self.location_input.text()
        tech_file = self.tech_file_input.text()
        netlist_file = self.netlist_file_input.text()
        project_file = os.path.join(location, f"{project_name}.icell")
        
        if os.path.exists(project_file):
            print(f"exits {project_file}")
            self.show_fail_info('Project exist, create Failed')
            return
        
        with open(project_file, 'w', encoding='utf-8') as fin:
            project = {'project_name': project_name, 'path': location, 'tech_file': tech_file, 'netlist_file': netlist_file}
            fin.write(json.dumps(project))
        self.close()

    def show_fail_info(self, info):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Warning") 
        msg_box.setText(info)
        msg_box.setStandardButtons(QMessageBox.Ok)

        msg_box.exec_()
