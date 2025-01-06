import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QToolBar, QAction, QPushButton, QGraphicsItem, QMenu
import qtawesome as qta


class Circuit(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Circuit", parent)

        # Initialize the widget for the dock window
        self.widget = QWidget(self)
        self.setWidget(self.widget)

        # Set up the layout
        self.dock_layout = QVBoxLayout(self.widget)
        
        # Create the graphics view and scene
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Create actions for zooming and resetting the view
        self.create_actions()

        # Create the custom toolbar (buttons for zoom, reset, etc.)
        self.dock_layout.addWidget(self.create_toolbar())  # Add toolbar to layout
        self.dock_layout.addWidget(self.view)  # Add view below the toolbar

        # Variable to hold the current SVG item
        self.current_svg_item = None
        
        # Mouse drag support variables
        self.dragging = False
        self.last_pos = None

    def create_actions(self):
        """Create actions for zooming and resetting the view"""
        self.zoom_in_action = QAction(qta.icon("fa.search-plus"), "", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.zoom_out_action = QAction(qta.icon("fa.search-minus"), "", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)

        self.reset_view_action = QAction(qta.icon("fa.refresh"), "", self)
        self.reset_view_action.triggered.connect(self.reset_view)

        self.fit_view_action = QAction(qta.icon("fa.expand"), "", self)
        self.fit_view_action.triggered.connect(self.fit_view)

    def create_toolbar(self):
        """Create a custom toolbar for the dock widget"""
        toolbar = QToolBar(self)  # Use QToolBar for standard toolbar
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # Set style for buttons
        toolbar.setIconSize(QSize(18, 18))
        
        # Add the actions to the toolbar
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_view_action)
        toolbar.addAction(self.fit_view_action)

        return toolbar

    def zoom_in(self):
        """Zoom in the view"""
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        """Zoom out the view"""
        self.view.scale(0.8, 0.8)

    def reset_view(self):
        """Reset the zoom level and position to the original (default) view"""
        # Reset any transformations applied (like zooming, rotation)
        self.view.resetTransform()
        
        # Optionally reset the scrollbars to their default positions (top-left)
        self.view.horizontalScrollBar().setValue(0)
        self.view.verticalScrollBar().setValue(0)
        
        # Optionally restore the default zoom level or transform settings
        # Reset to 1:1 scale (no zoom)
        self.view.scale(1, 1)
        
        # Set the view to the full scene's bounding rect
        if self.current_svg_item:
            self.view.setSceneRect(self.scene.sceneRect())  # Restore to the entire scene

    def fit_view(self):
        """Fit the view to the scene size"""
        if self.current_svg_item:
            self.view.fitInView(self.current_svg_item.boundingRect(), Qt.KeepAspectRatio)

    def load_svg(self, file_path):
        """Load an SVG file into the renderer and display it"""
        self.renderer = QSvgRenderer()  # Reinitialize the renderer each time to avoid issues
        if not self.renderer.load(file_path):
            print(f"Failed to load SVG file: {file_path}")
            return
        
        # Remove previous items if any
        if self.current_svg_item is not None:
            self.scene.removeItem(self.current_svg_item)

        # Create a new QGraphicsSvgItem with the renderer
        self.current_svg_item = QGraphicsSvgItem()
        self.current_svg_item.setSharedRenderer(self.renderer)
        self.current_svg_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        # self.current_svg_item.setTransformationMode(Qt.SmoothTransformation)

        self.scene.addItem(self.current_svg_item)
        # Scale the item to fit the view
        self.fit_view()
            
        
    # Handle mouse press event to initiate dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()

    # Handle mouse release event to stop dragging
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    # Handle mouse move event to drag the view
    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.last_pos
            self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() - delta.x())
            self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() - delta.y())
            self.last_pos = event.pos()

    # Handle wheel event for zooming
    def wheelEvent(self, event):
        zoom_factor = 1.1
        if event.angleDelta().y() < 0:
            zoom_factor = 0.9
        
        # Zoom the view in or out
        self.view.scale(zoom_factor, zoom_factor)

    # Optional: Handling right-click context menu for resetting the view
    def contextMenuEvent(self, event):
        menu = self.createContextMenu()
        menu.exec_(event.globalPos())

    def createContextMenu(self):
        menu = QMenu(self)
        reset_action = menu.addAction("Reset View")
        reset_action.triggered.connect(self.reset_view)
        return menu
