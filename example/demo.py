import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel
)
from PyQt5.QtCore import Qt, QDateTime

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI() 
        self.setWindowTitle(' 简易聊天室')
        self.resize(400,  500)

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 消息展示区域
        self.message_list  = QListWidget()
        self.message_list.setStyleSheet(""" 
            QListWidget {
                background-color: #F5F5F5;
                border-radius: 5px;
                padding: 10px;
            }
            QListWidget::item {
                margin: 5px;
                background: #FFFFFF;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        main_layout.addWidget(self.message_list) 

        # 输入区域布局
        input_layout = QHBoxLayout()

        # 输入框
        self.input_field  = QTextEdit()
        self.input_field.setMaximumHeight(100) 
        self.input_field.setAttribute(Qt.WA_InputMethodEnabled,  True)  # 显式启用输入法
        self.input_field.setPlaceholderText(" 输入消息...")
        self.input_field.setStyleSheet(""" 
            QTextEdit {
                border: 2px solid #0078D4;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        input_layout.addWidget(self.input_field) 

        # 发送按钮
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self.send_message) 
        send_btn.setStyleSheet(""" 
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #006CBB;
            }
        """)
        input_layout.addWidget(send_btn) 

        main_layout.addLayout(input_layout) 
        self.setLayout(main_layout) 

    def send_message(self):
        message = self.input_field.toPlainText().strip() 
        if message:
            # 创建消息气泡
            time_str = QDateTime.currentDateTime().toString("hh:mm:ss") 
            
            # 创建自定义的widget实现气泡效果
            item_widget = QWidget()
            item_layout = QVBoxLayout()
            
            time_label = QLabel(f"【你】{time_str}")
            time_label.setStyleSheet("color:  #666; font-size: 10px;")
            
            content_label = QLabel(message)
            content_label.setStyleSheet(""" 
                background: #0078D4;
                color: white;
                padding: 8px;
                border-radius: 5px;
                max-width: 300px;
            """)
            content_label.setWordWrap(True) 
            
            item_layout.addWidget(time_label) 
            item_layout.addWidget(content_label) 
            item_widget.setLayout(item_layout) 

            # 创建列表项并设置尺寸
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint()) 
            
            self.message_list.addItem(list_item) 
            self.message_list.setItemWidget(list_item,  item_widget)
            
            # 清空输入框并自动滚动到底部
            self.input_field.clear() 
            self.message_list.scrollToBottom() 

if __name__ == '__main__':   
    app = QApplication(sys.argv) 
    window = ChatWindow()
    window.show() 
    sys.exit(app.exec_()) 