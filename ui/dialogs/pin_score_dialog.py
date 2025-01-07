from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import qtawesome as qta 
from ui.icons import *

class PinScoreDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pin Assessment")
        self.setWindowIcon(qta.icon(M_TOOLS_PIN_ASSESS_ICON))
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        font = QFont("Roboto", 10)
        self.setFont(font)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(5, 5, 5, 5)
     
        title_label = QLabel("Pin Scores", self)
        title_label.setFont(QFont("Roboto", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
 
        main_layout.addWidget(title_label)

 
        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(2) 
        self.tree.setHeaderLabels(["Pin Name", "Score"])
        
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        main_layout.addWidget(self.tree)
        
        self.update_tree(data)


    def update_tree(self, data):
        self.tree.clear()
        for macro_name, pin_scores in data.items():
            macro_item = QTreeWidgetItem(self.tree)
            macro_item.setText(0, macro_name)
            macro_item.setFont(0, QFont("Roboto", 12, QFont.Bold))

            for pin_name, score in pin_scores.items():
                pin_item = QTreeWidgetItem(macro_item)
                pin_item.setText(0, pin_name)
                pin_item.setText(1, f"{score:.2f}")
                pin_item.setTextAlignment(1, Qt.AlignLeft)

            macro_item.setExpanded(True)
