from ui.icons import *
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import qtawesome as qta


class MacroScoreDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.update_table(data)

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Macro Assessment")
        self.setWindowIcon(qta.icon(M_TOOLS_MACRO_COST_ICON))
        self.setMinimumWidth(400)
        self.setFont(QFont("Roboto", 10))

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(5, 5, 5, 5)

        title_label = self._create_title_label()
        main_layout.addWidget(title_label)

        self.table = self._create_table()
        main_layout.addWidget(self.table)

    def _create_title_label(self):
        """Create and configure the title label."""
        title_label = QLabel("Macro Scores", self)
        title_label.setFont(QFont("Roboto", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        return title_label

    def _create_table(self):
        """Create and configure the QTableWidget."""
        table = QTableWidget(self)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Macro Name", "Score"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSortingEnabled(True)  # Enable sorting
        return table

    def update_table(self, data):
        """Update the table with new data."""
        self.table.setRowCount(len(data))
        for row, (macro_name, score) in enumerate(data.items()):
            self._add_table_row(row, macro_name, score)
        self.table.sortItems(1, Qt.AscendingOrder)

    def _add_table_row(self, row, macro_name, score):
        """Add a row to the table."""
        name_item = QTableWidgetItem(macro_name)
        name_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, name_item)

        score_item = QTableWidgetItem(f"{score:.2f}")
        score_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 1, score_item)
