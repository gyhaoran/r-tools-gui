from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import qtawesome as qta
from ui.icons import *


class MacroScoreDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Macro Assessment")
        self.setWindowIcon(qta.icon(M_TOOLS_MACRO_COST_ICON))
        self.setMinimumWidth(400)
        
        font = QFont("Roboto", 10)
        self.setFont(font)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(5, 5, 5, 5)

        title_label = QLabel("Macro Scores", self)
        title_label.setFont(QFont("Roboto", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Macro Name", "Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) 

        main_layout.addWidget(self.table)

        self.update_table(data)

    def update_table(self, data):
        self.table.setRowCount(len(data))
        for row, (macro_name, score) in enumerate(data.items()):
            # Macro Name
            name_item = QTableWidgetItem(macro_name)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, name_item)

            # Score
            score_item = QTableWidgetItem(f"{score:.2f}")
            score_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, score_item)
            