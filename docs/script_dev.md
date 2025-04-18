# pyqt5 gui cmos后端物理版图自动化设计应用（标准单元库布局布线）

现状
我们的软件目前支持对标准单元库布局、布线和重新布线，以及反向布线（从gds到gds），支持不同的布局布线算法和策略，布局布线的规则，对单元库的pin评估


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


class ProjectBrowser(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Project", parent=parent)
        self.tree_widget = QTreeWidget(self)


class ConsoleWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Console", parent=parent)
        self.console = QPlainTextEdit()


class PythonCodeEditor(QsciScintilla):
    pass
    

class ScriptDevWidget(QWidget):
    pass



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # 创建菜单栏和Scripts菜单
        main_menu = self.menuBar()
        scripts_menu = main_menu.addMenu("&Scripts")
        dev_action = QAction("Script Development", self)
        dev_action.triggered.connect(self.show_script_dev)
        scripts_menu.addAction(dev_action)
        
    def show_script_dev(self):
        widget = ScriptDevWidget()
        widget.show()


需求：
    帮我完成class ScriptDevWidget、ProjectBrowser、ConsoleWidget、PythonCodeEditor代码（用来帮助用户进行python脚本开发）
备注：
1. 这个脚本主要是用户可以通过我们提供open api支持对布局或者布线规则的定制，算法的自定义或者选择，脚本支持python原生语言
2. 我们的主程序支持运行用户输入的脚本

1. 顶部支持菜单栏：New、Open、| Go Back、Go Forward | Run、Debug
2. 左边支持project Browser
3. center部分是python代码编辑器，可以显示多个python文件，标题栏显示文件名（basename即可）（TextEditor功能， 最好支持python语言高亮，语法提示和补全）
4. 底部添加Console，用于显示脚本运行的日志


基于PyQt5和QScintilla开发， 输出完整的代码，写在一个文件中
1. 代码要求Clean code原则
2. 代码中的注释使用英文
3. 你的回答部分使用中文

