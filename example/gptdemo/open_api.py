import sys
import os
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, 
                            QFileDialog, QTextEdit, QMessageBox)
from PyQt5.QtCore import QObject, pyqtSignal

# ================= OpenAPI 实现 =================
class OpenAPI(QObject):
    api_called = pyqtSignal(str)  # API调用信号
    
    def __init__(self):
        super().__init__()
        self.netlist = 'test_case.sp'
        self.place_result = "place.json"
        self.place_call_back = None
        self.route_call_back = None
    
    def show_message(self, title, content):
        self.api_called.emit(f"{title} - {content}")
        
    def set_place_call_back(self, func):
        self.place_call_back = func
        
    def set_route_call_back(self, func):
        self.route_call_back = func

    def default_place(self, sp_file='test.sp'):
        self.show_message("Place", "iCell 默认布局算法")

    def default_route(self, place_file='place.json'):
        self.show_message("Route", "iCell 默认布线算法")    
        
    def apr(self):
        if self.place_call_back:
            self.show_message("Place", self.place_call_back(self.netlist))
        else:
            self.default_place()
            
        if self.route_call_back:
            self.show_message("Route", self.route_call_back(self.place_result))
        else:
            self.default_route()
        
    def run(self):
        self.show_message("Run", "iCell place route start")
        self.apr()
        self.show_message("Run", "iCell place route end")


# =============== 脚本执行引擎 ================
class ScriptExecutor(QObject):
    exec_result = pyqtSignal(str, int)  # (消息, 状态码)
    
    def __init__(self):
        super().__init__()
        self.api = OpenAPI()
        self.sandbox_env = {
            '__builtins__': __builtins__,
            'open_api': self.api,
            'print': self.safe_print
        }
    
    def safe_print(self, *args, **kwargs):
        output = ' '.join(map(str, args))
        self.exec_result.emit(f"[输出] {output}", 0)
    
    def _safety_trace(self, frame, event, arg):
        return self._safety_trace
    
    def run_python_code(self, code):
        sys.settrace(self._safety_trace)
        exec(code, self.sandbox_env)
        sys.settrace(None)        
        self.exec_result.emit("执行成功", 0)
    
    def run_script(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            self.run_python_code(code)           
        except Exception as e:
            error_msg = f"执行错误：{str(e)}\n{traceback.format_exc()}"
            self.exec_result.emit(error_msg, 1)

# =============== 主界面 ================
class ScriptRunnerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.executor = ScriptExecutor()
        self.executor.exec_result.connect(self.handle_result)
        self.executor.api.api_called.connect(self.log_api_call)
    
    def init_ui(self):
        # 主窗口设置
        self.setWindowTitle("PyQt5脚本运行器")
        self.setGeometry(300, 300, 800, 600)
        
        # 日志显示区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.setCentralWidget(self.log_area)
        
        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('脚本管理')
        
        # 导入动作
        import_action = QAction('导入脚本', self)
        import_action.triggered.connect(self.import_script)
        file_menu.addAction(import_action)
    
    def import_script(self):
        """导入脚本对话框"""
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(
            self, "选择Python脚本", "", 
            "Python Files (*.py);;All Files (*)", 
            options=options)
        
        if filepath:
            self.log_area.append(f"正在执行：{os.path.basename(filepath)}")
            self.executor.run_script(filepath)
    
    def handle_result(self, msg, code):
        """处理执行结果"""
        color = "green" if code == 0 else "red"
        self.log_area.append(f'<font color="{color}">{msg}</font>')
    
    def log_api_call(self, msg):
        """记录API调用"""
        self.log_area.append(f'<font color="blue">[API调用] {msg}</font>')

# =============== 启动程序 ================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScriptRunnerApp()
    window.show()
    sys.exit(app.exec_())
    
    
