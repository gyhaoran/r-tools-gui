from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QTreeView, QWidget


class Layer:
    def __init__(self, name, layer_type, color=None):
        self.name = name
        self.layer_type = layer_type
        self.color = color if color else QColor(Qt.black)
        self.visible = True

    def __repr__(self):
        return f"Layer(name={self.name}, type={self.layer_type}, visible={self.visible})"


class LayersWidget(QDockWidget):
    def __init__(self, layers, parent=None):
        super().__init__("Layers", parent)
        self.layers = layers
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.init_ui()
        self.populate_layers()

    def init_ui(self):
        self.widget = QWidget(self)
        self.setWidget(self.widget)
        self.layout = QVBoxLayout(self.widget)

        self.layers_tree = QTreeView(self.widget)
        self.layers_tree.setHeaderHidden(True)
        self.model = QStandardItemModel(self.layers_tree)
        self.layers_tree.setModel(self.model)
        self.layout.addWidget(self.layers_tree)

        self.layers_tree.clicked.connect(self.layer_clicked)

    def populate_layers(self):
        for layer in self.layers:
            layer_item = self.create_layer_item(layer)
            self.model.appendRow(layer_item)

    def create_layer_item(self, layer):
        layer_item = QStandardItem(layer.name)
        layer_item.setCheckable(True)
        layer_item.setCheckState(Qt.Checked if layer.visible else Qt.Unchecked)
        layer_item.setBackground(layer.color)
        layer_item.setData(layer)
        return layer_item

    def layer_clicked(self, index):
        item = self.model.itemFromIndex(index)
        layer = item.data()
        layer.visible = item.checkState() == Qt.Checked
        print(f"Layer {layer.name} visibility: {layer.visible}")
