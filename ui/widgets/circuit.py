import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QToolBar, QAction, QMenu, QGraphicsItem
import qtawesome as qta


class Circuit(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Circuit", parent)
        self.widget = QWidget(self)
        self.setWidget(self.widget)
        self.dock_layout = QVBoxLayout(self.widget)
        
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        
        self.current_svg_item = None
        self.dragging = False
        self.last_pos = None

        self.create_actions()
        self.dock_layout.addWidget(self.create_toolbar())
        self.dock_layout.addWidget(self.view)

    def create_actions(self):
        self.zoom_in_action = QAction(qta.icon("fa.search-plus"), "", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.zoom_out_action = QAction(qta.icon("fa.search-minus"), "", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)

        self.reset_view_action = QAction(qta.icon("fa.refresh"), "", self)
        self.reset_view_action.triggered.connect(self.reset_view)

        self.fit_view_action = QAction(qta.icon("fa.expand"), "", self)
        self.fit_view_action.triggered.connect(self.fit_view)

    def create_toolbar(self):
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(18, 18))
        
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_view_action)
        toolbar.addAction(self.fit_view_action)

        return toolbar

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(0.8, 0.8)

    def reset_view(self):
        self.view.resetTransform()
        self.reset_scrollbars()
        self.view.scale(1, 1)
        
        if self.current_svg_item:
            self.view.setSceneRect(self.scene.sceneRect())

    def reset_scrollbars(self):
        self.view.horizontalScrollBar().setValue(0)
        self.view.verticalScrollBar().setValue(0)

    def fit_view(self):
        if self.current_svg_item:
            self.view.fitInView(self.current_svg_item.boundingRect(), Qt.KeepAspectRatio)

    def load_svg(self, file_path):
        self.renderer = QSvgRenderer()
        if not self.renderer.load(file_path):
            print(f"Failed to load SVG file: {file_path}")
            return
        
        self.remove_current_svg_item()
        self.add_svg_item()
        self.fit_view()

    def remove_current_svg_item(self):
        if self.current_svg_item:
            self.scene.removeItem(self.current_svg_item)

    def add_svg_item(self):
        self.current_svg_item = QGraphicsSvgItem()
        self.current_svg_item.setSharedRenderer(self.renderer)
        self.current_svg_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.scene.addItem(self.current_svg_item)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.handle_drag(event)

    def handle_drag(self, event):
        delta = event.pos() - self.last_pos
        self.disable_scrollbars()
        self.adjust_scrollbars(delta)
        self.last_pos = event.pos()

    def disable_scrollbars(self):
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def adjust_scrollbars(self, delta):
        self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() - delta.x())
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() - delta.y())

    def wheelEvent(self, event):
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.view.scale(zoom_factor, zoom_factor)

    def contextMenuEvent(self, event):
        menu = self.create_context_menu()
        menu.exec_(event.globalPos())

    def create_context_menu(self):
        menu = QMenu(self)
        reset_action = menu.addAction("Reset View")
        reset_action.triggered.connect(self.reset_view)
        return menu
