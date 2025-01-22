from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton


class MacroInfoDialog(QDialog):
    def __init__(self, macro, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Macro Information")
        self.setGeometry(100, 100, 600, 400)

        self.init_ui()
        self.set_macro_info(macro)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

    def set_macro_info(self, macro):
        self.text_edit.setText(str(macro))
