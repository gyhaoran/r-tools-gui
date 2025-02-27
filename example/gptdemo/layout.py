import sys, os

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.colors import to_rgba
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout, QAction,
                             QDockWidget, QWidget, QListWidget, QListWidgetItem,QToolBar,
                             QStyle, QColorDialog, QStyledItemDelegate, QStyleOptionButton)
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QSize, QRect, QEvent, pyqtSignal
import qtawesome as qta

def rect_to_polygon(rect_pts):
    poly_pt = []
    pt1 = list(rect_pts[0])
    poly_pt.append(pt1)
    pt2 = [rect_pts[0][0], rect_pts[1][1]]
    poly_pt.append(pt2)
    pt3 = list(rect_pts[1])
    poly_pt.append(pt3)
    pt4 = [rect_pts[1][0], rect_pts[0][1]]
    poly_pt.append(pt4)
    return poly_pt

color_defs = {
    'BORDER': ('black', False), 
    'FIN': ('purple', True), 
    'MOI': ('red', True), 
    'MOC': ('red', True),
    'GT': ('green', True), 
    'AR': ('green', True), 
    'AA': ('orange', True), 
    'NW': ('cyan', False),
    'SN': ('cyan', False), 
    'SP': ('cyan', False),
    'LVT_N': ('cyan', False), 
    'LVT_P': ('cyan', False), 
    # 'SVT_N': ('cyan', False), 
    # 'SVT_P': ('cyan', False), 
    'GTC': ('magenta', True),
    'VOB': ('magenta', True), 
    'M1_E1': ('blue', True), 
    'M1_E2': ('blue', True), 
    'V0G_E1': ('brown', True),
    'V0G_E2': ('brown', True), 
    'VOI': ('pink', True), 
    'M1BA': ('gray', True), 
    'M1BB': ('gray', True),
    'M1TXT': ('black', True)
}

data = {
    "BORDER": [[(0, 0), (3150, 2520)]],
    "FIN": [[(0, 345), (3150, 430)], [(0, 660), (3150, 745)], 
            [(0, 1775), (3150, 1860)], [(0, 2090), (3150, 2175)]],
    "MOI": [[(210, 0), (420, 2520)], [(840, 0), (1050, 2520)], 
            [(1470, 0), (1680, 2520)], [(2100, 0), (2310, 2520)], 
            [(2730, 0), (2940, 2520)]],
    "MOC": [[(630, 70), (1260, 430)], [(2520, 430), (3150, 1875)], 
            [(630, 1875), (1890, 1875)], [(1260, 795), (1890, 1875)], 
            [(2520, 795), (3150, 1875)], [(630, 2090), (1260, 2450)], 
            [(1890, 2090), (2520, 2450)]],
    "GT": [[(-45, 0), (45, 2520)], [(585, 0), (675, 2520)], 
           [(1215, 0), (1305, 2520)], [(1845, 0), (1935, 2520)], 
           [(2475, 0), (2565, 2520)], [(3105, 0), (3195, 2520)]],
    "AR": [[(-45, 0), (45, 2520)], [(3105, 0), (3195, 2520)]],
    "AA": [[(0, 230), (3150, 860)], [(0, 1660), (3150, 2290)]],
    "NW": [[(-630, 1260), (3780, 3150)]],
    "SN": [[(0, 1260), (3150, 2520)]],
    "SP": [[(0, 0), (3150, 1260)]],
    "LVT_N": [[(0, 1260), (3150, 2520)]],
    "LVT_P": [[(0, 0), (3150, 1260)]],
    "GTC": [[(0, -115), (3150, 115)], [(0, 2405), (3150, 2635)]],
    "VOB": [[(0, -80), (3150, 80)], [(0, 2440), (3150, 2600)]],
    "M1_E1": [[(0, 810), (3150, 990)], [(0, 1530), (3150, 1710)]],
    "M1_E2": [[(0, -270), (3150, 270)], [(0, 450), (3150, 630)], 
              [(0, 1170), (3150, 1350)], [(0, 1890), (3150, 2070)], 
              [(0, 2250), (3150, 2790)]],
    "V0G_E1": [[(1180, 460), (1340, 620)], [(2440, 460), (2600, 620)]],
    "V0G_E2": [[(550, 460), (710, 620)], [(1810, 460), (1970, 620)]],
    "VOI": [[(865, 1180), (1025, 1340)], [(2125, 1180), (2285, 1340)]],
    "M1BA": [[(-110, 520), (110, 2000)], [(3040, 520), (3260, 2000)]],
    "M1BB": [[(-110, 160), (110, 2360)], [(3040, 160), (3260, 2360)]],
    "M1TXT": [[(1, -269)], [(1, 2251)], [(2520, 540)], [(2205, 1260)]]
}

text_def = ['VSS', 'VDD', 'I', 'ZN']

class LayerShapes:
    def __init__(self, type: int, points, txt=''):
        self.type = type
        self.points = points
        self.text = txt

def create_shapes(points):
    shapes = []
    i = 0
    for point in points:
        if len(point) == 1:
            shapes.append(LayerShapes(1, point, text_def[i]))
            i += 1
        elif len(point) == 2:
            shapes.append(LayerShapes(2, point))
        elif len(point) > 2:
            shapes.append(LayerShapes(3, point))
    return shapes

def build_data():
    layer_shapes = {}
    for key, points in data.items():
        layer_shapes[key] = create_shapes(points)
    return layer_shapes

class LayerDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkbox_size = 20  # Checkbox size
        self.color_rect_width = 20  # Color block width
        self.item_padding = 5  # Item spacing

    def paint(self, painter, option, index):
        """Draw list item"""
        painter.save()
        self._setup_painter(painter, option, index)
        self._draw_background(painter, option, index)
        self._draw_color_block(painter, option, index)
        self._draw_checkbox(painter, option, index)
        self._draw_layer_name(painter, option, index)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        """Handle user interaction events"""
        if event.type() == QEvent.MouseButtonPress:
            if self._is_color_block_clicked(event, option):
                self._handle_color_change(index)
                return True
            if self._is_checkbox_clicked(event, option):
                self._handle_fill_toggle(index)
                return True
        elif event.type() == QEvent.MouseButtonDblClick:
            self._handle_visibility_toggle(index)
            return True
        return super().editorEvent(event, model, option, index)

    def _setup_painter(self, painter, option, index):
        """Configure common painter settings"""
        painter.setRenderHint(QPainter.Antialiasing)
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

    def _draw_background(self, painter, option, index):
        """Draw selected background"""
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

    def _draw_color_block(self, painter, option, index):
        """Draw color block"""
        color = index.data(Qt.UserRole + 1)
        color_rect = self._get_color_block_rect(option)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(color_rect)

    def _draw_checkbox(self, painter, option, index):
        """Draw checkbox"""
        checkbox_rect = self._get_checkbox_rect(option)
        opt = QStyleOptionButton()
        opt.rect = checkbox_rect
        opt.state = QStyle.State_Enabled | QStyle.State_Active
        if index.data(Qt.UserRole + 3):  # Fill state
            opt.state |= QStyle.State_On
        QApplication.style().drawControl(QStyle.CE_CheckBox, opt, painter)

    def _draw_layer_name(self, painter, option, index):
        """Draw layer name"""
        layer_name = index.data(Qt.DisplayRole)
        visible = index.data(Qt.UserRole + 2)
        text_rect = self._get_text_rect(option)
        text_color = QColor(Qt.black) if visible else QColor(Qt.gray)
        font = painter.font()
        font.setStrikeOut(not visible)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, layer_name)

    def _get_color_block_rect(self, option):
        """Get the rectangle area of the color block"""
        return QRect(
            option.rect.x() + self.item_padding,
            option.rect.y() + self.item_padding,
            self.color_rect_width,
            option.rect.height() - 2 * self.item_padding
        )

    def _get_checkbox_rect(self, option):
        """Get the rectangle area of the checkbox"""
        return QRect(
            option.rect.right() - self.checkbox_size - self.item_padding,
            option.rect.y() + (option.rect.height() - self.checkbox_size) // 2,
            self.checkbox_size,
            self.checkbox_size
        )

    def _get_text_rect(self, option):
        """Get the rectangle area of the text"""
        color_rect = self._get_color_block_rect(option)
        checkbox_rect = self._get_checkbox_rect(option)
        return QRect(
            color_rect.right() + self.item_padding,
            option.rect.y(),
            checkbox_rect.left() - color_rect.right() - 2 * self.item_padding,
            option.rect.height()
        )

    def _is_color_block_clicked(self, event, option):
        """Check if the color block is clicked"""
        color_rect = self._get_color_block_rect(option)
        return color_rect.contains(event.pos())

    def _is_checkbox_clicked(self, event, option):
        """Check if the checkbox is clicked"""
        checkbox_rect = self._get_checkbox_rect(option)
        return checkbox_rect.contains(event.pos())

    def _handle_color_change(self, index):
        """Handle color change event"""
        old_color = index.data(Qt.UserRole + 1)
        new_color = QColorDialog.getColor(QColor(old_color), self.parent())
        if new_color.isValid():
            self.parent().colorChanged.emit(index.data(Qt.DisplayRole), new_color.name())

    def _handle_fill_toggle(self, index):
        """Handle fill state toggle event"""
        fill = not index.data(Qt.UserRole + 3)
        self.parent().fillToggled.emit(index.data(Qt.DisplayRole), fill)

    def _handle_visibility_toggle(self, index):
        """Handle visibility toggle event"""
        visible = not index.data(Qt.UserRole + 2)
        self.parent().visibilityToggled.emit(index.data(Qt.DisplayRole), visible)
        
        
class LayersWidget(QWidget):
    colorChanged = pyqtSignal(str, str)
    visibilityToggled = pyqtSignal(str, bool)
    fillToggled = pyqtSignal(str, bool)

    def __init__(self, color_defs, visible_layers, parent=None):
        super().__init__(parent)
        self.list_widget = QListWidget()
        self.list_widget.setItemDelegate(LayerDelegate(self))
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        for layer in color_defs:
            color, fill = color_defs[layer]
            item = QListWidgetItem(layer)
            item.setData(Qt.UserRole + 1, color)
            item.setData(Qt.UserRole + 2, visible_layers[layer])
            item.setData(Qt.UserRole + 3, fill)
            self.list_widget.addItem(item)

    def update_color(self, layer, color):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.text() == layer:
                item.setData(Qt.UserRole + 1, color)
                self.list_widget.viewport().update()

    def update_visibility(self, layer, visible):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.text() == layer:
                item.setData(Qt.UserRole + 2, visible)
                self.list_widget.viewport().update()

    def update_fill(self, layer, fill):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.text() == layer:
                item.setData(Qt.UserRole + 3, fill)
                self.list_widget.viewport().update()

class LayoutWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_color = '#FFFFFF'
        self.figure = Figure(figsize=(12, 9))
        self.canvas = FigureCanvas(self.figure)
        self.color_defs = {}
        self.visible_layers = {}
        self.create_actions()
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.create_toolbar())
        layout.addWidget(self.canvas)
        self.set_theme(False)
        
        self.selected_patch = None
        self.original_edge_color = None
        self.original_linestyle = None
        self.ax = None  # 保存当前绘图区域
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.installEventFilter(self)   # 添加事件过滤器
        self.drag_start  = None
        self.drag_origin  = None
        self.canvas.mpl_connect('button_press_event',  self.on_drag_start) 
        self.canvas.mpl_connect('motion_notify_event',  self.on_drag_move) 
        self.canvas.mpl_connect('button_release_event',  self.on_drag_end) 

    def create_actions(self):
        self.zoom_in_action = QAction(qta.icon("fa.search-plus"), "", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.zoom_out_action = QAction(qta.icon("fa.search-minus"), "", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)

        self.fit_view_action = QAction(qta.icon("fa.expand"), "", self)
        self.fit_view_action.triggered.connect(self.fit_view)

    def create_toolbar(self):
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(18, 18))
        
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.fit_view_action)

        return toolbar

    def zoom_in(self):
        if self.ax is None:
            return
        
        # 获取当前的x和y轴范围
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # 计算新的范围，缩小范围以实现放大效果
        x_center = sum(xlim) / 2
        y_center = sum(ylim) / 2
        new_width = (xlim[1] - xlim[0]) * 0.8  # 缩小20%
        new_height = (ylim[1] - ylim[0]) * 0.8  # 缩小20%
        
        # 设置新的范围
        self.ax.set_xlim(x_center - new_width / 2, x_center + new_width / 2)
        self.ax.set_ylim(y_center - new_height / 2, y_center + new_height / 2)
        
        # 重新绘制画布
        self.canvas.draw_idle()

    def zoom_out(self):
        if self.ax is None:
            return
        
        # 获取当前的x和y轴范围
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # 计算新的范围，扩大范围以实现缩小效果
        x_center = sum(xlim) / 2
        y_center = sum(ylim) / 2
        new_width = (xlim[1] - xlim[0]) * 1.2  # 扩大20%
        new_height = (ylim[1] - ylim[0]) * 1.2  # 扩大20%
        
        # 设置新的范围
        self.ax.set_xlim(x_center - new_width / 2, x_center + new_width / 2)
        self.ax.set_ylim(y_center - new_height / 2, y_center + new_height / 2)
        
        # 重新绘制画布
        self.canvas.draw_idle()

    def fit_view(self):
        if self.ax is None:
            return
        
        # 自动调整视图范围
        self.ax.autoscale()
        
        # 重新绘制画布
        self.canvas.draw_idle()

    def on_drag_start(self, event):
        """处理拖动开始事件"""
        if event.button  == 1 and QApplication.keyboardModifiers()  & Qt.ControlModifier:
            self.drag_start  = (event.x, event.y)
            self.drag_origin  = (self.ax.get_xlim(),  self.ax.get_ylim()) 
            self.setCursor(Qt.ClosedHandCursor) 
            return True
        return False

    def on_drag_move(self, event):
        """处理拖动过程事件"""
        if self.drag_start  and event.inaxes  == self.ax: 
            dx = (event.x - self.drag_start[0])  * 0.80  # 灵敏度调节系数
            dy = (self.drag_start[1]  - event.y) * 0.80
            
            xlim = (self.drag_origin[0][0]  - dx, 
                    self.drag_origin[0][1]  - dx)
            ylim = (self.drag_origin[1][0]  + dy, self.drag_origin[1][1]  + dy)
            
            self.ax.set_xlim(xlim) 
            self.ax.set_ylim(ylim) 
            self.canvas.draw_idle() 

    def on_drag_end(self, event):
        """处理拖动结束事件"""
        if event.button  == 1:
            self.drag_start  = None
            self.setCursor(Qt.ArrowCursor) 


    def eventFilter(self, obj, event):
        """ 事件过滤器处理canvas的滚轮事件 """
        if obj == self.canvas  and event.type()  == QEvent.Wheel:
            if QApplication.keyboardModifiers()  & Qt.ControlModifier:
                self.handle_zoom(event) 
                return True  # 事件已处理
        return super().eventFilter(obj, event)
    
    def handle_zoom(self, event):
        """ 执行缩放操作 """
        delta = event.angleDelta().y() 
        if delta == 0:
            return
        
        # 计算缩放因子（滚轮向上放大，向下缩小）
        scale_factor = 0.9 if delta > 0 else 1.1
        
        ax = self.ax 
        if not ax:
            return
        
        # 保持中心点不变进行缩放
        xlim = ax.get_xlim() 
        ylim = ax.get_ylim() 
        x_center = sum(xlim)/2
        y_center = sum(ylim)/2
        new_width = (xlim[1]-xlim[0]) * scale_factor
        new_height = (ylim[1]-ylim[0]) * scale_factor
        
        ax.set_xlim(x_center  - new_width/2, x_center + new_width/2)
        ax.set_ylim(y_center  - new_height/2, y_center + new_height/2)
        self.canvas.draw_idle() 
           
    def on_pick(self, event):
        """处理形状选中事件"""
        if self.selected_patch is not None:
            # 恢复之前选中的形状
            self.selected_patch.set_edgecolor(self.original_edge_color)
            self.selected_patch.set_linestyle(self.original_linestyle)
        # 获取当前选中的形状
        self.selected_patch = event.artist
        self.original_edge_color = self.selected_patch.get_edgecolor()
        self.original_linestyle = self.selected_patch.get_linestyle()
        # 设置高亮
        self.selected_patch.set_edgecolor('white')
        self.selected_patch.set_linestyle('-')  # 实线
        self.canvas.draw_idle()

    def on_click(self, event):
        """处理点击空白区域事件"""
        if event.inaxes != self.ax or self.ax is None:
            return
        # 检查是否点击了任何形状
        for patch in self.ax.patches:
            if patch.contains(event)[0]: 
                return
        # 恢复所有形状
        if self.selected_patch is not None:
            self.selected_patch.set_edgecolor(self.original_edge_color)
            self.selected_patch.set_linestyle(self.original_linestyle)
            self.selected_patch = None
            self.canvas.draw_idle()
            
    def set_theme(self, dark_mode):
        bg_color = '#19232D'
        self.text_color = '#FFFFFF'
        self.figure.patch.set_facecolor(bg_color)
        self.canvas.setStyleSheet(f"background-color: {bg_color};")
        self.update_text_colors(self.text_color)
        self.canvas.draw_idle()

    def update_text_colors(self, text_color):
        for ax in self.figure.axes:
            ax.title.set_color(text_color)
            for spine in ax.spines.values():
                spine.set_edgecolor(to_rgba(text_color, alpha=0.5))

    def draw_text(self, ax, text, color):
        ax.annotate(text.text, xy=text.points[0], color=color, size=15, zorder=10)

    def draw_box(self, ax, box, color, fill):
        points = rect_to_polygon(box.points)
        shape = plt.Polygon(points, closed=True, fill=fill, linewidth=2, linestyle=':', color=color, alpha=0.75, zorder=10)
        shape.set_picker(5)
        ax.add_patch(shape)

    def draw_polygon(self, ax, polygon, color, fill):
        shape = plt.Polygon(polygon.points, closed=True, fill=fill, linewidth=2, linestyle=':', color=color, alpha=0.75, zorder=10)
        shape.set_picker(5)
        ax.add_patch(shape)

    def draw_subplot(self, ax, shapes, color, fill):
        for shape in shapes:
            if shape.type == 1:
                self.draw_text(ax, shape, color)
            elif shape.type == 2:
                self.draw_box(ax, shape, color, fill)
            elif shape.type == 3:
                self.draw_polygon(ax, shape, color, fill)

    def draw_layout(self, title, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(
            left=0,    # 左边界比例
            right=1,   # 右边界比例
            bottom=0.01,  # 底部边界比例
            top=0.95,     # 顶部保留标题空间
            wspace=0,     # 水平子图间距
            hspace=0      # 垂直子图间距
        )
        # ax.set_title(title, color=self.text_color)
        ax.set_axis_off()
        ax.set_aspect('equal')
        self.ax = ax
        for layer, shapes in data.items():
            if self.visible_layers.get(layer, True):
                try:
                    color, fill = self.color_defs.get(layer, ('gray', True))
                except Exception as e:
                    print(f"layer: {layer}, {self.color_defs.get(layer, ('gray', True))}, {e}")
                self.draw_subplot(ax, shapes, color, fill)
        
        ax.autoscale_view()
        self.canvas.draw()

    def draw(self, title, data, color_defs, visible_layers):
        self.color_defs = color_defs
        self.visible_layers = visible_layers
        self.draw_layout(title, data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.color_defs = {k: (v[0], v[1]) for k, v in color_defs.items()}
        self.visible_layers = {layer: True for layer in data.keys()}
        
        self.layout_win = LayoutWindow(self)
        self.setCentralWidget(self.layout_win)
        
        self.layers_widget = LayersWidget(self.color_defs, self.visible_layers)
        dock = QDockWidget("Layers", self)
        dock.setWidget(self.layers_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        
        self.layers_widget.colorChanged.connect(self.update_color)
        self.layers_widget.visibilityToggled.connect(self.update_visibility)        
        self.layers_widget.fillToggled.connect(self.update_fill) 
        
        self.load() 

    def load(self):
        layer_shapes = build_data()
        self.layout_win.draw('INVD4',  layer_shapes, self.color_defs,  self.visible_layers) 

    def update_color(self, layer, color):
        self.color_defs[layer] = (color, self.color_defs[layer][1])
        self.layers_widget.update_color(layer,  color)
        self.load() 

    def update_visibility(self, layer, visible):
        print(f"layer: {layer}, visible: {visible}")
        self.visible_layers[layer]  = visible
        self.layers_widget.update_visibility(layer,  visible)
        self.load() 

    def update_fill(self, layer, fill):       
        self.color_defs[layer] = (self.color_defs[layer][0], fill)
        self.layers_widget.update_fill(layer,  fill)
        self.load()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    