# script_ide.py
import sys
import os
import re
import traceback
from PyQt5.QtCore import Qt, QFileInfo, QDir, pyqtSignal, QObject, QFile, QThreadPool, QThread, QTimer, pyqtSlot
from PyQt5.QtWidgets import (QWidget, QMainWindow, QVBoxLayout, QApplication, QDockWidget, QFileDialog, QLineEdit, QTreeWidgetItem,
                             QHBoxLayout, QCheckBox, QPushButton, QDialog, QTabWidget,
                             QToolBar, QTreeWidget, QStyle, QMenu, QInputDialog, QLineEdit, QAction, QPlainTextEdit, QMessageBox, QShortcut)
from PyQt5.QtGui import QFont, QKeySequence, QTextCharFormat, QColor
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
import qtawesome as qta



style_map = {
    QsciLexerPython.Comment: "注释",
    QsciLexerPython.Number: "数字",
    QsciLexerPython.DoubleQuotedString: "双引号字符串",
    QsciLexerPython.SingleQuotedString: "单引号字符串",
    QsciLexerPython.Keyword: "关键字",
    QsciLexerPython.TripleSingleQuotedString: "三单引号字符串",
    QsciLexerPython.TripleDoubleQuotedString: "三双引号字符串",
    QsciLexerPython.ClassName: "类名",
    QsciLexerPython.FunctionMethodName: "函数方法名",
    QsciLexerPython.Operator: "运算符",
    QsciLexerPython.Identifier: "标识符",
    QsciLexerPython.CommentBlock: "块注释",
    QsciLexerPython.UnclosedString: "未闭合字符串",
    QsciLexerPython.HighlightedIdentifier: "高亮标识符",
    QsciLexerPython.Decorator: "装饰器",
    QsciLexerPython.DoubleQuotedFString: "双引号f-string",
    QsciLexerPython.SingleQuotedFString: "单引号f-string",
    QsciLexerPython.TripleSingleQuotedFString: "三单引号f-string",
    QsciLexerPython.TripleDoubleQuotedFString: "三双引号f-string"
}


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

class PythonExecutor():
    """Core Python executor with structured return values"""
    
    def __init__(self, open_api, logger=print):
        self.api = open_api
        self.sandbox_env = {
            '__builtins__': __builtins__,
            '__name__': '__main__',
            'open_api': self.api,
            'print': logger,
        } 

    def regex_extract_line(self, error_msg: str) -> int:
        pattern = r"""
            line\s+(\d+)    # match line x
            |         
            $(\w+\.\w+),\s+line\s+(\d+)$  # match (filename.py, line x)
        """
        match = re.search(pattern, error_msg, re.VERBOSE)
        if match:
            return int(match.group(1) or match.group(3))
        return 0
        
    def _handle_exception(self, exc: Exception) -> tuple:
        """
        Process exceptions with error code classification
        Returns: (error_code, line_number: int, error_type: str, detail: str)
        eg exc: Missing parentheses in call to 'print'. Did you mean print(...)? (new_script.py, line 6)
        """
        error_str = str(exc)
        error_line = self.regex_extract_line(error_str)
        error_type = str(type(exc))
        return (1, error_line, error_type, error_str)  # Error code 1 for exceptions
    
    def execute(self, code: str, file_name: str='<user_code>') -> tuple:
        """
        Execute Python code with structured return format
        Returns: (error_code, line_number: int, error_type: str, detail: str)
        """
        try:
            self.sandbox_env.update({'__file__': file_name})
            compiled = compile(code, file_name, 'exec')
            exec(compiled, self.sandbox_env)
            return (0, 0, '', '')  # Success
        except Exception as e:
            return self._handle_exception(e)
    
    def run_script(self, filepath: str):
        """
        Execute Python script from file
        :param filepath: Path to Python script file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return self.execute(f.read(), filepath)
        except Exception as e:
            error_msg = f"[System Error] {str(e)}\n{traceback.format_exc()}"
            return (1, 0, error_msg)  # Error in file reading


class WorkerThread(QThread):
    result_ready = pyqtSignal(int, int, str, str)
    
    def __init__(self, executor:PythonExecutor, code, filename):
        super().__init__()
        self.executor = executor 
        self.code = code
        self.filename = filename

    def run(self):
        try:           
            result = self.executor.execute(self.code, self.filename)
            self.result_ready.emit(*result)
        except Exception as e:
            self.result_ready.emit(3, -1, "ScriptRunningException", str(e))
    
    def stop(self):
        try:
            self.terminate()
            self.wait(1000)
            self.result_ready.emit(0, 0, "ExecutionStopped", "Script execution stopped")            
        except Exception as e:
            self.result_ready.emit(3, -1, "ScriptStopException", str(e))    


class ScriptExecutor(QObject):
    """Qt adapter layer with signal enhancement"""
    exec_result = pyqtSignal(int, int, str, str)  # (code, line, detail, msg)
    output_signal = pyqtSignal(str)  # For print output
        
    def __init__(self):
        super().__init__()
        self.api = OpenAPI()
        self._executor = PythonExecutor(self.api, self._capture_print)
        self._current_thread = None

    def _capture_print(self, *args):
        """Intercept print output and emit as signal"""
        output = ' '.join(map(str, args))
        self.output_signal.emit(f"[Output] {output}")          
          
    def run_code(self, code: str, file_name: str):
        self._current_thread = WorkerThread(self._executor, code, file_name)
        self._current_thread.result_ready.connect(self.exec_result.emit)
        self._current_thread.finished.connect(self._current_thread.deleteLater) 
        self._current_thread.start()
          
    def run_script(self, filepath: str):
        """
        Execute Python script from file
        :param filepath: Path to Python script file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.run_code(f.read(), filepath)
        except Exception as e:
            error_msg = f"[System Error] {str(e)}\n{traceback.format_exc()}"
            self.exec_result.emit(1, 0, error_msg, "Error in file reading")

    def stop(self):
        if self._current_thread:
            self._current_thread.stop()
            self._current_thread = None
            
        
#region Project Browser Implementation
class ProjectBrowser(QDockWidget):
    def __init__(self, work_dir, script_dev_window=None):
        super().__init__("Script Browser", parent=script_dev_window)
        self._work_dir = work_dir
        self._sd_window = script_dev_window
        self._init_icons()
        self._setup_ui(work_dir)
        self._setup_connections()
        self.setFeatures(QDockWidget.DockWidgetMovable)

    def _init_icons(self):
        """Initialize QtAwesome icons"""
        self.folder_icon = qta.icon('fa5s.folder', color='#F5A623') # 黄色
        self.open_folder_icon = qta.icon('fa5s.folder-open', color='#F5A623') 
        self.py_file_icon = qta.icon('fa5s.file-code', color='#4A90E2') # 蓝色

    def _setup_ui(self, work_dir):
        widget = QWidget(self)
        self.setWidget(widget)
        layout = QVBoxLayout(widget)

        self.path_bar = QLineEdit()
        self.path_bar.setToolTip("WorkDir")
        self.path_bar.setPlaceholderText("WorkDir")
        
        choose_folder_btn = QAction(self.style().standardIcon(QStyle.SP_DirOpenIcon), "", self)
        refresh_btn = QAction(self.style().standardIcon(QStyle.SP_BrowserReload), "", self)
        self.path_bar.addAction(choose_folder_btn, QLineEdit.TrailingPosition)
        self.path_bar.addAction(refresh_btn, QLineEdit.TrailingPosition)
        choose_folder_btn.triggered.connect(self.choose_work_dir)
        refresh_btn.triggered.connect(self.refresh_tree)
        layout.addWidget(self.path_bar)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.tree)

        self.update_work_dir(work_dir)
        
    def _setup_connections(self):
        self.tree.itemDoubleClicked.connect(self._on_item_double_click)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)

    def _filter_python_files(self, entry):
        return entry.fileName().endswith(('.py', '.pyw'))

    def _populate_tree(self, path):
        self.tree.clear()
        self.path_bar.setText(QDir.toNativeSeparators(path))
        self.root_item = QTreeWidgetItem(self.tree, [QDir(path).dirName()])
        self.root_item.setData(0, Qt.UserRole, path)
        self._set_folder_icon_animation(self.root_item)
        self._add_tree_items(self.root_item, path)
        self.tree.expandAll()

    def _add_tree_items(self, parent_item, path):
        """Add directory contents with icons"""
        dir = QDir(path)
        entries = dir.entryInfoList(QDir.AllEntries | QDir.NoDotAndDotDot,QDir.DirsFirst | QDir.Name)
        
        for entry in filter(self._filter_python_files, entries):
            item = QTreeWidgetItem(parent_item, [entry.fileName()])
            item.setData(0, Qt.UserRole, entry.absoluteFilePath())
            self._set_file_icon(item)
                
    def _set_file_icon(self, item):
        item.setIcon(0, self.py_file_icon)

    def update_wokrdir_icon(self):
        index = self.tree.indexFromItem(self.root_item)
        self.root_item.setIcon(0, self.open_folder_icon if self.tree.isExpanded(index) else self.folder_icon)
            
    def _set_folder_icon_animation(self, item):
        tree = self.tree                   
        tree.expanded.connect(self.update_wokrdir_icon)
        tree.collapsed.connect(self.update_wokrdir_icon)        
        index = tree.indexFromItem(item)
        item.setIcon(0, self.open_folder_icon if tree.isExpanded(index) else self.folder_icon)
        
    def _on_item_double_click(self, item, column):
        path = item.data(0, Qt.UserRole)
        if QFileInfo(path).isFile():
            self._open_file_in_editor(path)

    def _open_file_in_editor(self, path):
        for i in range(self._sd_window.editor_widget.count()):
            if self._sd_window.editor_widget.tabText(i) == QFileInfo(path).fileName():
                self._sd_window.editor_widget.setCurrentIndex(i)
                return
        self._sd_window.load_file(path)

    def _show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
            
        menu = QMenu()
        path = item.data(0, Qt.UserRole)
        
        if QFileInfo(path).isFile():
            open_action = menu.addAction("Open")
            rename_action = menu.addAction("Rename")
            delete_action = menu.addAction("Delete")
            
            open_action.triggered.connect(lambda: self._open_file_in_editor(path))
            rename_action.triggered.connect(lambda: self._rename_item(item))
            delete_action.triggered.connect(lambda: self._delete_item(item))
        else:
            new_file_action = menu.addAction("New File")
            new_file_action.triggered.connect(lambda: self._create_new_file(item))
            
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def _rename_item(self, item):
        old_path = item.data(0, Qt.UserRole)
        new_name, ok = QInputDialog.getText(
            self, "Rename", "New name:", text=QFileInfo(old_path).fileName()
        )
        if ok and new_name:
            new_path = QDir(QFileInfo(old_path).path()).filePath(new_name)
            if QFile.rename(old_path, new_path):
                item.setText(0, new_name)
                item.setData(0, Qt.UserRole, new_path)

    def _delete_item(self, item):
        path = item.data(0, Qt.UserRole)
        if QFileInfo(path).isFile():
            is_open = any(
                self._sd_window.editor_widget.widget(i).file_path == path 
                for i in range(self._sd_window.editor_widget.count())
            )
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            if is_open:
                msg.setText("file is open, confirm delete?")
                msg.setInformativeText(f"Delete file {QFileInfo(path).fileName()}?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            else:
                msg.setInformativeText(f"Delete file {QFileInfo(path).fileName()}")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            if msg.exec_() == (QMessageBox.Yes if is_open else QMessageBox.Ok):
                if is_open:
                    for i in range(self._sd_window.editor_widget.count()):
                        if self._sd_window.editor_widget.widget(i).file_path == path:
                            self._sd_window.editor_widget.close_tab(i)
                QFile.remove(path)
                item.parent().removeChild(item)
                
    def _create_new_file(self, parent_item, text="new_script.py"):
        dir_path = parent_item.data(0, Qt.UserRole)
        name, ok = QInputDialog.getText(self, "New File", "File name:", text=text)
        if ok and name:
            if not name.endswith('.py'): 
                name += '.py'
            file_path = QDir(dir_path).filePath(name)
            if os.path.exists(file_path):
                QMessageBox.warning(self, "File Exists", "File already exists.")
                self._create_new_file(parent_item, name)
            else:
                QFile(file_path).open(QFile.WriteOnly)
                self.refresh_tree()

    def update_work_dir(self, work_dir):
        if os.path.isdir(work_dir):
            self._work_dir = work_dir
            self._populate_tree(work_dir)
            
    def refresh_tree(self):
        path = self.path_bar.text()
        self.update_work_dir(path)
        
    def choose_work_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Choose Work Directory", self._work_dir)
        if path:
            self.update_work_dir(path)

#endregion

#region Console Implementation
class ConsoleWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Console", parent)
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.setWidget(self.console)
        self.console.setContextMenuPolicy(Qt.CustomContextMenu)
        self.console.customContextMenuRequested.connect(self._show_context_menu)
        self.setFeatures(QDockWidget.DockWidgetMovable)
        self.default_format = QTextCharFormat()
        self.default_format.setForeground(QColor(Qt.GlobalColor.black))
        
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor(Qt.GlobalColor.red))
        
    def _show_context_menu(self, pos):
        menu = self.console.createStandardContextMenu()
        menu.addSeparator()

        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self._clear_console)
        menu.addAction(clear_action)        
        menu.exec(self.console.viewport().mapToGlobal(pos)) 

    def _clear_console(self):
        self.console.clear()
                
    def append_output(self, text):
        """Append text to console with default style"""
        self.console.appendPlainText(text)
        
    def append_error(self, text):
        """Append error message with red color"""
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.End)
        
        # 应用错误格式
        cursor.setCharFormat(self.error_format)
        cursor.insertText(text + '\n')
        
        # 显式恢复默认格式 [1](@ref)
        cursor.setCharFormat(self.default_format)
        self.console.setTextCursor(cursor)
#endregion

#region Python Editor Implementation
class PythonCodeEditor(QsciScintilla):
    def __init__(self, path, editor_widget=None):
        super().__init__(parent=editor_widget)
        self.editor_widget = editor_widget  # Parent window reference
        self.file_path = path
        self._load_file(path)
        self._init_ui()
        
        # Search-related variables
        self.search_text = ""
        self.match_case = False
        self.whole_word = False
        self.last_search_pos = -1

    def change_font_size(self, size):
        self.base_font.setPixelSize(size)
        
    def _init_ui(self):
        """Initialize editor UI components"""
        # Configure Python lexer
        self.lexer = QsciLexerPython(self)
        self.base_font = QFont("Consolas", 9)
        self.lexer = QsciLexerPython(self)
        self.lexer.setDefaultFont(self.base_font)        
        self.setLexer(self.lexer)

        # Editor configuration
        self.setAutoIndent(True)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        self.setUtf8(True)
        self.setEdgeColumn(160)
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        # 设置默认缩放为150%
        self.SendScintilla(QsciScintilla.SCI_SETZOOM, 5)

        # Auto-completion setup     
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)

        # API setup for autocomplete
        self.api = QsciAPIs(self.lexer)
        self._load_apis()
        self.api.prepare()

        # Line number margin
        self.setMarginsFont(QFont("Consolas", 9))
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)

        # Initialize search shortcuts
        self._init_search_shortcuts()
        self._init_modified_tracking()
        

    def _init_search_shortcuts(self):
        """Bind search-related keyboard shortcuts"""
        # Ctrl+F for find dialog
        self.find_shortcut = QShortcut(QKeySequence.Find, self)
        self.find_shortcut.activated.connect(self.show_find_dialog)

    def show_find_dialog(self):
        """Display advanced find dialog with search options"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Find")
        layout = QVBoxLayout(dialog)

        self.search_input = QLineEdit(self.selectedText())
        layout.addWidget(self.search_input)

        # Options checkboxes
        options_layout = QHBoxLayout()
        self.case_checkbox = QCheckBox("Match case")
        self.whole_word_checkbox = QCheckBox("Whole word")
        options_layout.addWidget(self.case_checkbox)
        options_layout.addWidget(self.whole_word_checkbox)
        layout.addLayout(options_layout)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.find_btn = QPushButton("Find")
        self.find_btn.clicked.connect(lambda: self.start_search(
            self.search_input.text(),
            self.case_checkbox.isChecked(),
            self.whole_word_checkbox.isChecked()
        ))
        btn_layout.addWidget(self.find_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()

    def start_search(self, search_text, match_case=False, whole_word=False, is_retry=False):
        """Initialize search with given parameters"""
        if not search_text:
            return
        self.search_text = search_text
        if not is_retry:
            self.last_search_pos = 0
        
        # Configure search flags
        search_flags = 0
        if match_case:
            search_flags |= QsciScintilla.SCFIND_MATCHCASE
        if whole_word:
            search_flags |= QsciScintilla.SCFIND_WHOLEWORD
        
        # Perform initial search
        found = self.findFirst(search_text, False, match_case, whole_word, True, True, self.last_search_pos, -1, False, search_flags)

        if found:
            line_from, index_from, line_to, index_to = self.getSelection()
            self.setSelection(line_from, index_from, line_to, index_to)
            self.last_search_pos = index_to
        else:
            QMessageBox.information(self, "Find", "Text not found")
            self.last_search_pos = -1

    def _load_file(self, path):
        """Load file content into editor"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.setText(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open file: {str(e)}")

    def _init_modified_tracking(self):
        self.textChanged.connect(self._on_text_modified)
        self._is_modified = False

    def _on_text_modified(self):
        if not self._is_modified:
            self._is_modified = True
            self._update_tab_title()
            
    def _update_tab_title(self):
        index = self.editor_widget.indexOf(self)
        if index == -1:
            return
        tab_text = self.editor_widget.tabText(index)
        if not tab_text.startswith('*'):
            self.editor_widget.setTabText(index, '*' + tab_text)
            
    def _load_apis(self):
        """Load Python API for autocompletion"""
        keywords = list(__builtins__.__dict__.keys())
        for keyword in keywords:
            self.api.add(keyword)
        self.api.add("open_api")
        self.api.add("open_api.apr")
        self.api.add("open_api.run")
    
    def save(self):
        with open(self.file_path, 'w') as f:
            f.write(self.text())
        self._is_modified = False

    def is_modified(self):
        return self._is_modified

    def keyPressEvent(self, event):
        """Override key events for better search navigation"""
        if event.key() == Qt.Key_Escape and self.search_text:
            self.clearSearchIndicators()
        super().keyPressEvent(event)

    def clearSearchIndicators(self):
        """Clear search highlight indicators"""
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
        self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.length())
        
#endregion


class EditorWidget(QTabWidget):
    """Editor widget for script development"""
    def __init__(self, sd_win=None):
        super().__init__(parent=sd_win)
        self.setWindowTitle("Script Editor")
        self.sd_win = sd_win
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def close_tab(self, index):
        editor = self.widget(index)
        if editor:
            if editor.is_modified():
                reply = QMessageBox.question(self, "Unsaved Changes", "You have unsaved changes. Do you want to save them?", 
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if reply == QMessageBox.Yes:
                    editor.save()
                elif reply == QMessageBox.Cancel:
                    return
            self.removeTab(index)
            editor.deleteLater()
    
    def open_file(self, path):
        """Open a file in the editor"""           
        tab_name = QFileInfo(path).fileName()
        for i in range(self.count()):
            if self.tabText(i) == tab_name:
                self.setCurrentIndex(i)
                return
            
        editor = PythonCodeEditor(path, self)
        self.addTab(editor, tab_name)
        self.setCurrentWidget(editor)

    def save_file(self):
        current_editor = self.currentWidget()
        if current_editor:
            try:
                current_editor.save()
                index = self.indexOf(current_editor)
                tab_text = self.tabText(index)
                if tab_text.startswith('*'):
                    self.setTabText(index, tab_text[1:])
            except Exception as e:
                QMessageBox.critical(self, "file save error:", f"{str(e)}")
            

class ScriptDevWindow(QMainWindow):
    """Main window for script development"""   
    def __init__(self, work_dir=str, parent=None):
        super().__init__(parent=parent)
        self.work_dir = work_dir
        self._init_ui()
        
        self._current_file = None
        self.running = False
        self.script_executor = ScriptExecutor()
        self.script_executor.output_signal.connect(self.console.append_output, Qt.QueuedConnection)
        self.script_executor.exec_result.connect(self.handle_exec_result, Qt.QueuedConnection)

    def _init_ui(self):       
        # Create toolbars
        self._init_toolbar()
        
        # Create project browser
        self.project_browser = ProjectBrowser(self.work_dir, self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_browser)
        
        # Create editor area
        self.editor_widget = EditorWidget(self)
        self.setCentralWidget(self.editor_widget)
        self.editor_widget.currentChanged.connect(self._on_editor_tab_changed)
        
        # Create console
        self.console = ConsoleWidget()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console)

        self.setWindowTitle("Script Development")
        self.resize(800, 600)
    
    def _on_editor_tab_changed(self, index):
        """Handle editor tab change event"""
        if index != -1:
            editor = self.editor_widget.widget(index)
            if isinstance(editor, PythonCodeEditor):
                self._current_file = editor.file_path
                self.console.append_output(f"Current file: {self._current_file}")
            else:
                self._current_file = None
        else:
            self._current_file = None
        self._enable_disable_run_action()
    
    def _enable_disable_run_action(self):
        if self.running:
            self.run_action.setEnabled(True)
        elif self._current_file:
            self.run_action.setEnabled(True)
        else:
            self.run_action.setEnabled(False)
    
    def create_action(self, name, icon, function, checkable=False, checked=False):
        action = QAction(qta.icon(icon), name, self)
        action.triggered.connect(function)
        action.setCheckable(checkable)
        action.setChecked(checked)
        return action
    
    def _create_actions(self):
        self.open_action = self.create_action("&Open...", 'fa.file-o', self.open_file)
        self.open_action.setShortcut(QKeySequence.Open)
        self.save_action = self.create_action("&Save", 'fa.save', self.save_file)
        self.save_action.setShortcut(QKeySequence.Save)
        self.run_action = self.create_action("&Run", 'msc.play', self.run_script)
        self.run_action.setShortcut(QKeySequence("Ctrl+R"))
        
        self.print_lexer_font_action = self.create_action("Print", "fa5s.print", self._print_lexer_font)
        self.print_lexer_font_action.setShortcut(QKeySequence("Ctrl+P"))
    
    def _print_lexer_font(self):
        current_editor = self.editor_widget.currentWidget()
        if current_editor and isinstance(current_editor, PythonCodeEditor):
            for style, _ in style_map.items():
                font = current_editor.lexer.font(style)
                print(f"Lexer: {style}, Font: {font.family()}, Size: {font.pointSize()}")
        else:
            print("No editor selected or invalid editor type.")
        
    def _init_toolbar(self):
        # Main toolbar
        self._create_actions()
        
        toolbar = QToolBar("Main Toolbar")
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.run_action)
        toolbar.addSeparator()
        toolbar.addAction(self.print_lexer_font_action)
        self.addToolBar(toolbar)
    
    def handle_exec_result(self, code, line, error_type, detail):
        """Handle execution results and display in console"""
        if not self.running: return
        if code == 0:
            self.console.append_output("Success.\n")
        else:
            self.console.append_error(f"[Error] Line {line}: {error_type} {detail}")
    
    def load_file(self, path):
        try:
            self.editor_widget.open_file(path)
            self._current_file = path
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open file: {str(e)}")    
        
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Python Script", "", "Python Files (*.py)")
        if path:
            self.load_file(path)
            
    def save_file(self):
        self.editor_widget.save_file()

    def update_running_state(self):
        self.running = not self.running
        if self.running:
            self.run_action.setIcon(qta.icon('msc.stop', color='red'))
            self.run_action.setText("Stop")
            self.run_action.setShortcut(QKeySequence("Ctrl+T"))
            self.run_action.triggered.connect(self.stop_script)
        else:
            self.run_action.setIcon(qta.icon('msc.play', color='green'))
            self.run_action.setText("Run")
            self.run_action.setShortcut(QKeySequence("Ctrl+R"))
            self.run_action.triggered.connect(self.run_script)
    
    def stop_script(self):
        if self.running:
            self.console.append_output("Stop script...\n")       
            self.script_executor.stop()
            self.update_running_state()

    def run_script(self):
        current_editor = self.editor_widget.currentWidget()
        if current_editor and not self.running:
            self.console.append_output("Running script...\n")            
            self.script_executor.run_code(current_editor.text(), self._current_file)
            self.update_running_state()
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create menu bar
        menubar = self.menuBar()
        scripts_menu = menubar.addMenu("&Scripts")
        
        # Script development action
        self.dev_action = QAction("Script Development", self)
        self.dev_action.triggered.connect(self.show_script_window)
        scripts_menu.addAction(self.dev_action)

        # Main window settings
        self.setWindowTitle("Physical Design Automation")
        self.setGeometry(100, 100, 1280, 720)

    def show_script_window(self):
        """Show script development window"""
        widget = ScriptDevWindow(os.getcwd(), self)
        widget.show()
        widget.raise_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    main_win.show_script_window()
    sys.exit(app.exec_())
    
