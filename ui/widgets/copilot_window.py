import json
import asyncio
from core import library_manager
from core.llm_client import LLMClient
from core.window import AbstractWindow, W_COPILOT_CHAT_ID
from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QTextEdit, QMenu, QApplication,
                             QHBoxLayout, QPushButton, QScrollArea, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QObject, QTimer, QEvent
from PyQt5.QtGui import QColor, QFont
import qtawesome as qta
import uuid
from qasync import asyncSlot

class EnhancedTextEdit(QTextEdit):
    """Enhanced text input box with improved IME support"""
    enterPressed = pyqtSignal()
    shiftEnterPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("微软雅黑", 11))
        self.setPlaceholderText("输入您的消息（Shift+Enter换行）...")
        self.setMinimumHeight(40)
        self.setMaximumHeight(120)
        self.setStyleSheet("""
            QTextEdit {
                border-radius: 0px;
                padding: 6px;
                background: #FFFFFF;
            }
        """)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.setInputMethodHints(Qt.ImhMultiLine)
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                self.shiftEnterPressed.emit()
                super().keyPressEvent(event)
            else:
                self.enterPressed.emit()
                event.accept()
        else:
            super().keyPressEvent(event)


class ChatMessageWidget(QTextEdit):
    """Chat message bubble widget with streaming display support"""
    def __init__(self, text, is_user=True, copilot_widget=None):
        super().__init__(parent=copilot_widget)
        self.is_user = is_user
        self.full_content = text
        self.copilot_widget: CopilotWidget = copilot_widget
        self.displayed_content = ""
        self.setReadOnly(True)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self._init_style()
        
        if is_user:
            self.setPlainText(text)
            self.adjust_size()
            return
        
        # Streaming display timer
        self.stream_timer = QTimer(self)
        self.stream_timer.timeout.connect(self._stream_display)
        self.display_position = 0        
        self.stream_speed = 20
        self.chunk_size = 10
        self._start_streaming()

    def _init_style(self):
        self.setStyleSheet(f"""
            background: {'#E8F5E9' if self.is_user else '#F5F5F5'};
            border-radius: 8px;
            padding: 12px;
            margin: 4px {'8px 0px 4px' if self.is_user else '0px 0px 4px'};
            white-space: pre-wrap;
        """)
        
    def _insert_content(self, new_content):
        cursor = self.textCursor()            
        cursor.movePosition(cursor.End)
        cursor.insertText(new_content)            
    
    def _stream_display(self):
        try:
            if self.display_position >= len(self.full_content):
                self.stream_timer.stop()
                self.adjust_size()
                return

            end_pos = min(self.display_position + self.chunk_size, len(self.full_content))            
            new_content = self.full_content[self.display_position:end_pos]
            self.display_position = end_pos
            self._insert_content(new_content)
            self.adjust_size()
        except Exception as e:
            self.stream_timer.stop()

    def _start_streaming(self):
        if len(self.full_content) > 0:
            self.stream_timer.start(self.stream_speed)

    def append_content(self, new_content):
        try:
            new_content = str(new_content) if new_content is not None else ""
            self.full_content += new_content
            
            if not self.stream_timer.isActive():
                self._start_streaming()
                
        except Exception as e:
            print(f"append content error: {str(e)}")

    def adjust_size(self):
        """Dynamic adjustment of widget size"""
        doc = self.document().clone()
        max_width = int(self.copilot_widget.width() * 0.75)
        doc.setTextWidth(max_width)
        doc_width = int(min(doc.idealWidth() + 40, max_width))
        doc_height = int(doc.size().height() + 30)
        self.setFixedWidth(doc_width)
        self.setFixedHeight(doc_height)
        self.copilot_widget.scroll_to_bottom()

    def sizeHint(self):
        return QSize(self.width(), self.height())

    def stop(self):
        """Stop streaming display"""
        self.stream_timer.stop()
        self._insert_content('\n\n已停止处理\n')
        self.adjust_size()
    
class CopilotWidget(QDockWidget):
    """AI Assistant interaction interface with enhanced streaming support"""
    sendRequest = pyqtSignal(dict, bool)  # (message content, deep mode)
    stopProcessing = pyqtSignal(str, bool)  # (request_id, deep_mode)

    def __init__(self, parent=None):
        super().__init__("AI Copilot", parent)
        self.current_request_id = None
        self.is_processing = False
        self.current_ai_message = None  # Track current AI message widget
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Initialize UI components"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(4)

        # Chat history area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_container)

        # Input panel
        input_panel = self.create_input_panel()

        main_layout.addWidget(self.scroll_area, 1)
        main_layout.addWidget(input_panel, 0)
        self.setWidget(main_widget)

    def create_input_panel(self):
        """Create input control panel"""
        panel = QWidget()
        panel.setStyleSheet("background: #F5F5F5; border-radius: 8px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.input_field = EnhancedTextEdit()
        control_layout = self.create_control_buttons()

        layout.addWidget(self.input_field)
        layout.addLayout(control_layout)
        return panel

    def create_control_buttons(self):
        """Create bottom control buttons"""
        self.deep_toggle = QPushButton("深度思考")
        self.init_deep_toggle()

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(qta.icon("ph.stop-circle", color="#E53935"))
        self.stop_btn.setIconSize(QSize(28, 28))
        self.stop_btn.setToolTip("停止当前处理")
        self.stop_btn.hide()

        self.send_btn = QPushButton()
        self.send_btn.setIcon(qta.icon("ph.paper-plane-tilt", color="#1E88E5"))
        self.send_btn.setIconSize(QSize(28, 28))
        self.send_btn.setToolTip("发送消息（Enter）")

        layout = QHBoxLayout()
        layout.addWidget(self.deep_toggle)
        layout.addStretch()
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.send_btn)
        return layout

    def init_deep_toggle(self):
        """Initialize deep mode toggle"""
        self.deep_toggle.setCheckable(True)
        self.deep_toggle.setIcon(qta.icon("ph.circle-wavy-question-light", color="#757575"))
        self.deep_toggle.setIconSize(QSize(24, 24))
        self.deep_toggle.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #757575;
                padding: 6px 12px;
                border: 1px solid #BDBDBD;
                border-radius: 16px;
            }
            QPushButton:checked {
                background: #E3F2FD;
                color: #1E88E5;
                border-color: #90CAF9;
            }
        """)

    def setup_connections(self):
        """Setup signal connections"""
        self.send_btn.clicked.connect(self.process_input)
        self.input_field.enterPressed.connect(self.process_input)
        self.stop_btn.clicked.connect(self.handle_stop)
        self.deep_toggle.toggled.connect(self.update_deep_mode_ui)

    def update_deep_mode_ui(self, enabled):
        """Update deep mode UI state"""
        color = "#1E88E5" if enabled else "#757575"
        self.deep_toggle.setIcon(qta.icon("ph.circle-wavy-question-light", color=color))
        self.deep_toggle.setToolTip("深度思考模式（已启用）" if enabled else "深度思考模式（未启用）")

    def process_input(self):
        """Process user input"""
        if self.is_processing:
            self.show_temporary_status("请等待当前请求完成", "#FFF3E0")
            return

        if message := self.input_field.toPlainText():
            self.commit_new_request(message)
        else:
            self.show_temporary_status("消息不能为空", "#FFEBEE")

    def commit_new_request(self, message):
        """Commit new request"""
        self._add_user_message(message)  # 改为使用新的用户消息添加方法
        self.input_field.clear()
        self.set_processing_state(True)
        self.current_request_id = str(uuid.uuid4())
        self.current_ai_message = None
        data = {"request_id": self.current_request_id, "content": message}
        self.sendRequest.emit(data, self.deep_toggle.isChecked())

    def _add_user_message(self, content):
        """添加用户消息（右侧对齐）"""
        message_widget = ChatMessageWidget(content, True, self)
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.addStretch(1)  # 添加弹性空间使消息靠右
        layout.addWidget(message_widget, 0, Qt.AlignRight)
        self.chat_layout.insertWidget(self.chat_layout.count()-1, container)
        self.scroll_to_bottom()

    def _add_ai_message(self, content):
        """添加AI消息（左侧对齐）"""
        self.current_ai_message = ChatMessageWidget(content, False, self)
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.addWidget(self.current_ai_message, 1, Qt.AlignLeft)
        layout.addStretch(0)
        self.chat_layout.insertWidget(self.chat_layout.count()-1, container)
        self.scroll_to_bottom()

    def handle_response(self, success, response, request_id, is_end=False):
        """Handle business layer response with partial updates"""
        if request_id != self.current_request_id:
            return

        if success:
            self.handle_success(response)
        else:
            self.handle_error(response)

        if is_end:
            self.set_processing_state(False)
            self.current_ai_message.adjust_size()
            self.current_request_id = None
            self.current_ai_message = None

    def handle_success(self, response):
        if self.current_ai_message:
            self._append_to_existing_message(response)
        else:
            self._add_ai_message(response)
    
    def _append_to_existing_message(self, content):
        """Append content to existing AI message"""
        self.current_ai_message.append_content(content)
        self.current_ai_message.adjust_size()
        self.scroll_to_bottom()

    def _add_message_widget(self, message_widget):
        """Add message widget to chat layout"""
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.addWidget(message_widget, 1, Qt.AlignLeft)
        layout.addStretch(0)
        self.chat_layout.insertWidget(self.chat_layout.count()-1, container)
        self.scroll_to_bottom()

    def handle_error(self, error_msg):
        """Display error message"""
        error_widget = ChatMessageWidget(f"请求异常: {error_msg}", False, self)
        error_widget.setStyleSheet("background-color: #FFEBEE;" + error_widget.styleSheet())
        self._add_message_widget(error_widget)

    def handle_stop(self):
        """Handle stop request"""
        if self.current_request_id:
            self.stopProcessing.emit(self.current_request_id, self.deep_toggle.isChecked())
            if self.current_ai_message:
                self.current_ai_message.stop()
            self.set_processing_state(False)
            self.current_request_id = None

    def set_processing_state(self, active):
        """Update processing state"""
        self.is_processing = active
        self.send_btn.setVisible(not active)
        self.stop_btn.setVisible(active)
        self.input_field.setReadOnly(active)
        self.input_field.setPlaceholderText("正在处理您的请求..." if active else "输入您的消息（Shift+Enter换行）...")

    def scroll_to_bottom(self):
        """Scroll to bottom of chat history"""
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def show_temporary_status(self, text, bg_color="#FFF3E0"):
        """Show temporary status message"""
        status = QLabel(text)
        status.setStyleSheet(f"""
            background: {bg_color};
            color: #5D4037;
            padding: 8px;
            border-radius: 6px;
            margin: 8px;
        """)
        self.chat_layout.insertWidget(0, status)
        QTimer.singleShot(3000, status.deleteLater)

    def update_status(self, status):
        """Update connection status"""
        self.setWindowTitle(f"AI Copilot - {status}")

class CopilotWindow(AbstractWindow):
    def __init__(self, parent=None):
        super().__init__(W_COPILOT_CHAT_ID)
        self._widget  = CopilotWidget(parent)
        self.llm_client  = LLMClient("ws://localhost:8765")
        self.llm_client.connect_server() 
        self.setup_connections()

    def setup_connections(self):
            # 添加调试输出
        print("Signal signature:", self._widget.sendRequest.signal)
        self._widget.sendRequest.connect(self.handle_request)
        self._widget.stopProcessing.connect(self.handle_stop) 
        
        self.llm_client.response_received.connect(self.handle_response)
        self.llm_client.connection_changed.connect(self._widget.update_status)
        self.llm_client.send_error.connect(self._widget.show_temporary_status)

    @asyncSlot(dict, bool)
    async def handle_request(self, data: dict, deep_mode: bool):
        """统一的异步请求处理"""
        try:
            # 添加数据校验
            if not isinstance(data, dict) or "content" not in data:
                raise ValueError("Invalid request format")
                
            # 调用LLM客户端
            request_id = await self.llm_client.send_request({
                "request_id": data.get("request_id", str(uuid.uuid4())),
                "content": data["content"]
            }, deep_mode)
            
            # 更新界面状态
            self._widget.current_request_id = request_id
            
        except Exception as e:
            self._widget.show_temporary_status(f"Error: {str(e)}")

    def handle_response(self, data):
        """响应处理保持兼容"""
        # 原数据格式保持不变
        self._widget.handle_response(
            success=True,
            response=data.get("content", ""),
            request_id=data.get("request_id", ""),
            is_end=data.get("is_end", True)
        )

    @asyncSlot(str, bool)
    async def handle_stop(self, request_id, deep_mode):
        """异步终止请求"""
        await self.llm_client.stop_request(request_id)
        if request_id in self._widget.active_requests:
            self._widget.active_requests.remove(request_id)
 
    def widget(self):
        return self._widget 
 
    def area(self):
        return Qt.LeftDockWidgetArea 
 
    def is_center(self):
        return False
