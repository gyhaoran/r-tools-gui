import sys
import os
import json
import qtawesome as qta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFileDialog, QDialog, QLabel, QFrame,
    QHBoxLayout, QSpacerItem, QSizePolicy, QDesktopWidget, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class NewProjectDialog(QDialog):
    QSS_STYLE_CREATE = """
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
                background-color: #D3D3D3; /* Gray background when disabled */
            }
        """
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setGeometry(0, 0, 600, 450)
        self.move_to_center()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        self.main_layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.setup_title()
        self.setup_project_name_input()
        self.setup_location_input()
        self.setup_tech_file_input()
        self.setup_netlist_file_input()

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setup_create_button()
        self.setLayout(self.main_layout)
        self.update_create_button_state()

    def setup_title(self):
        """Setup the title label and separator."""
        title_label = QLabel("Create New Project", self)
        title_label.setFixedHeight(50)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(separator)

    def setup_project_name_input(self):
        """Setup the project name input field."""
        self.project_name = QLineEdit(self)
        self.project_name.setPlaceholderText("Input Project Name")
        self.project_name.setText("New_Project")
        self.project_name.setFixedWidth(200)
        self.project_name.textChanged.connect(self.update_create_button_state)
        self.form_layout.addRow("Project Name:", self.project_name)

    def setup_location_input(self):
        """Setup the project location input field and browse button."""
        self.location_input = QLineEdit(self)
        self.location_input.setPlaceholderText('Select Project Path')
        self.location_input.setText(os.path.expanduser('~'))

        self.browse_location_btn = QPushButton(self)
        self.browse_location_btn.setIcon(qta.icon('fa.folder-o'))
        self.browse_location_btn.clicked.connect(self.browse_location)

        location_layout = QHBoxLayout()
        location_layout.addWidget(self.location_input)
        location_layout.addWidget(self.browse_location_btn)
        self.form_layout.addRow("Location:", location_layout)

    def setup_tech_file_input(self):
        """Setup the tech file input field and browse button."""
        self.tech_file_input = QLineEdit(self)
        self.tech_file_input.setPlaceholderText("Select Tech File")
        self.tech_file_input.textChanged.connect(self.update_create_button_state)

        self.browse_tech_btn = QPushButton(self)
        self.browse_tech_btn.setIcon(qta.icon('fa.folder-o'))
        self.browse_tech_btn.clicked.connect(self.browse_tech_file)

        tech_layout = QHBoxLayout()
        tech_layout.addWidget(self.tech_file_input)
        tech_layout.addWidget(self.browse_tech_btn)
        self.form_layout.addRow("Tech File:", tech_layout)

    def setup_netlist_file_input(self):
        """Setup the netlist file input field and browse button."""
        self.netlist_file_input = QLineEdit(self)
        self.netlist_file_input.setPlaceholderText("Select Netlist File")
        self.netlist_file_input.textChanged.connect(self.update_create_button_state)

        self.browse_netlist_btn = QPushButton(self)
        self.browse_netlist_btn.setIcon(qta.icon('fa.folder-o'))
        self.browse_netlist_btn.clicked.connect(self.browse_netlist_file)

        netlist_layout = QHBoxLayout()
        netlist_layout.addWidget(self.netlist_file_input)
        netlist_layout.addWidget(self.browse_netlist_btn)
        self.form_layout.addRow("Netlist File:", netlist_layout)

    def setup_create_button(self):
        """Setup the create button and its layout."""
        self.create_btn = QPushButton("Create", self)
        self.create_btn.setStyleSheet(self.QSS_STYLE_CREATE)
        self.create_btn.clicked.connect(self.create_project)

        # Create a horizontal layout for the Create button
        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.create_btn)

        # Add the button layout to the main layout
        self.main_layout.addLayout(button_layout)

    def move_to_center(self):
        """Move the dialog to the center of the screen."""
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def browse_location(self):
        """Open a dialog to select the project location."""
        folder = QFileDialog.getExistingDirectory(self, "Select Project Location")
        if folder:
            self.location_input.setText(folder)
            self.update_create_button_state()

    def browse_tech_file(self):
        """Open a dialog to select the tech file."""
        file, _ = QFileDialog.getOpenFileName(self, "Select Tech File", "", "Tech Files (*.tech);;All Files (*)")
        if file:
            self.tech_file_input.setText(file)
            self.update_create_button_state()

    def browse_netlist_file(self):
        """Open a dialog to select the netlist file."""
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
        project_name = self.project_name.text()
        location = self.location_input.text()
        tech_file = self.tech_file_input.text()
        netlist_file = self.netlist_file_input.text()
        project_file = os.path.join(location, f"{project_name}.icell")

        if os.path.exists(project_file):
            self.show_fail_info('Project exists, creation failed')
            return
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                project = {'project_name': project_name, 'path': location,'tech_file': tech_file, 'netlist_file': netlist_file}
                json.dump(project, f)
            self.close()
        except Exception as e:
            self.show_fail_info(f"Failed to create project: {str(e)}")

    def show_fail_info(self, info):
        """Show a warning message box with the given info."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Warning")
        msg_box.setText(info)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        