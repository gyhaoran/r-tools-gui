from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton


class MacroInfoDialog(QDialog):
    """
    A dialog to display information about a Macro object.
    """
    def __init__(self, macro, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Macro Information")
        self.setGeometry(100, 100, 600, 400)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Text area to display Macro information
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.text_edit)

        # Close button
        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        # Set the Macro information
        self.set_macro_info(macro)

    def set_macro_info(self, macro):
        """
        Set the Macro information to display in the dialog.
        :param macro: A Macro object.
        """
        self.text_edit.setText(str(macro))
