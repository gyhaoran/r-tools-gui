from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QTreeView, QCheckBox, QWidget


class Layer:
    """Layer class to hold information for each layer"""
    def __init__(self, name, layer_type, color=None):
        self.name = name
        self.layer_type = layer_type  # e.g. 'metal', 'via', 'pin', 'obs'
        self.color = color if color else QColor(Qt.black)  # Default to black
        self.visible = True  # Layer visibility flag
    
    def __repr__(self):
        return f"Layer(name={self.name}, type={self.layer_type}, visible={self.visible})"
    

class LayersWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Layers", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Initialize layout and main widget
        self.widget = QWidget(self)
        self.setWidget(self.widget)
        self.layout = QVBoxLayout(self.widget)
        
        # Create a tree view for the layers list
        self.layers_tree = QTreeView(self.widget)
        self.layers_tree.setHeaderHidden(True)
        
        # Create a model to hold layers
        self.model = QStandardItemModel(self.layers_tree)
        self.layers_tree.setModel(self.model)
        icon = QIcon()

        self.layout.addWidget(self.layers_tree)
        
        # Sample layers
        self.layers = [
            Layer("Metal1", "metal", QColor(240, 0, 0)),  # Red for Metal1
            Layer("Metal2", "metal", QColor(0, 240, 0)),  # Green for Metal2
            Layer("Via1", "via", QColor(0, 0, 240)),      # Blue for Via1
            Layer("Metal1.Pin", "pin", QColor(255, 255, 0)),    # Yellow for Pin1
        ]
        
        self.populate_layers()

    def populate_layers(self):
        """Populate the layers in the QTreeView"""
        for layer in self.layers:
            layer_item = QStandardItem(layer.name)
            layer_item.setCheckable(True)
            layer_item.setCheckState(Qt.Checked if layer.visible else Qt.Unchecked)
            # Set color as the background of the item
            layer_item.setBackground(layer.color)
            
            # Add to the model
            self.model.appendRow(layer_item)
            layer_item.setData(layer)  # Store Layer object as data

        # Connect signal for checking/unchecking layers
        self.layers_tree.clicked.connect(self.layer_clicked)

    def layer_clicked(self, index):
        """Handle the event when a layer is clicked (show/hide layer)"""
        item = self.model.itemFromIndex(index)
        layer = item.data()  # Retrieve the Layer object
        
        layer.visible = item.checkState() == Qt.Checked
        print(f"Layer {layer.name} visibility: {layer.visible}")

