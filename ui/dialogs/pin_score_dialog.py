from ui.icons import *
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


class PinScoreDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.update_tree(data)

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Pin Assessment")
        self.setWindowIcon(qta.icon(M_TOOLS_PIN_ASSESS_ICON))
        self.setMinimumWidth(300)
        self.setFont(QFont("Roboto", 10))

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Title Label
        title_label = self._create_title_label()
        main_layout.addWidget(title_label)

        # Tree Widget
        self.tree = self._create_tree_widget()
        main_layout.addWidget(self.tree)

    def _create_title_label(self):
        """Create and configure the title label."""
        title_label = QLabel("Pin Scores", self)
        title_label.setFont(QFont("Roboto", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        return title_label

    def _create_tree_widget(self):
        """Create and configure the QTreeWidget."""
        tree = QTreeWidget(self)
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Pin Name", "Score"])
        tree.setSortingEnabled(True)  # Enable sorting

        header = tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        return tree

    def update_tree(self, data):
        """Update the tree with new data."""
        self.tree.clear()
        for macro_name, pin_scores in data.items():
            macro_item = self._create_macro_item(macro_name)
            self._add_pin_items(macro_item, pin_scores)
            macro_item.setExpanded(True)

    def _create_macro_item(self, macro_name):
        """Create and configure a macro-level QTreeWidgetItem."""
        macro_item = QTreeWidgetItem(self.tree)
        macro_item.setText(0, macro_name)
        return macro_item

    def _add_pin_items(self, macro_item, pin_scores):
        """Add pin-level QTreeWidgetItems under a macro item."""
        for pin_name, score in pin_scores.items():
            pin_item = QTreeWidgetItem(macro_item)
            pin_item.setText(0, pin_name)
            pin_item.setText(1, f"{score:.2f}")
            pin_item.setTextAlignment(1, Qt.AlignLeft)