from PyQt5.QtWidgets import QDockWidget, QListView, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class ViewBrowser(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("View Browser", parent=parent)

        self.widget = QWidget(self)
        self.setWidget(self.widget)

        layout = QVBoxLayout(self.widget)
        
        tree_widget = QTreeWidget(self)
        tree_widget.setHeaderLabels(["Library"])
        
        root1 = QTreeWidgetItem(tree_widget, ["Library1"])
        QTreeWidgetItem(root1, ["Cell1"])
        QTreeWidgetItem(root1, ["Cell2"])
        
        root2 = QTreeWidgetItem(tree_widget, ["Library2"])
        QTreeWidgetItem(root2, ["Cell1"])
        QTreeWidgetItem(root2, ["Cell2"])

        layout.addWidget(tree_widget)
        