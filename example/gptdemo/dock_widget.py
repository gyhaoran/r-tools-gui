import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QPushButton, QLabel, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

class DraggableDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Draggable Dialog')
        self.setGeometry(300, 300, 300, 200)
        # self.setWindowFlags(Qt.FramelessWindowHint)  # 去掉标题栏
        self.setWindowFlags(Qt.Window)
        self.label = QLabel('This is a draggable dialog!', self)
        self.label.move(50, 50)
        
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.label)
        
        self.mouse_press_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()  # 记录鼠标按下时的全局位置

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_press_pos:
            delta = event.globalPos() - self.mouse_press_pos
            self.move(self.pos() + delta)  # 移动窗口
            self.mouse_press_pos = event.globalPos()  # 更新按下时的位置

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 600, 400)

        self.button = QPushButton('Open Draggable Dialog', self)
        self.button.clicked.connect(self.open_dialog)
        self.button.setGeometry(50, 50, 200, 50)

    def open_dialog(self):
        self.dialog = DraggableDialog()
        self.dialog.show()  # 弹出对话框

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
