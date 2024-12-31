# ui/dialogs/open_file_dialog.py

from PyQt5.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class OpenFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open File")
        self.setGeometry(100, 100, 300, 100)

        self._init_ui()

    def _init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)

        # Create the open file dialog button
        open_button = QPushButton("Open File", self)
        open_button.clicked.connect(self.open_file)
        layout.addWidget(open_button)

    def open_file(self):
        """Open file dialog to select files."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;SP Files (*.sp);;GDS Files (*.gds)", options=options)
        if file_name:
            print(f"File opened: {file_name}")
            self.accept()
            