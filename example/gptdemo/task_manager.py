import sys
import time
import random
import qtawesome as qta
from collections import deque
from PyQt5.QtCore import (Qt, QObject, QThread, pyqtSignal, QMutex, QMutexLocker, QDateTime, QProcess, QTimer)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QAction, QHBoxLayout, QPushButton,
                             QTreeWidgetItem, QDockWidget, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget,
                             QHeaderView, QStyleFactory)
import subprocess

#region Constants and Enums
class TaskStatus:
    PENDING = ("Pending", "#FFD700")    # Gold
    RUNNING = ("Running", "#1E90FF")    # Dodger Blue
    COMPLETED = ("Completed", "#32CD32")# Lime Green
    CANCELED  = ("Canceled", "#FF5722")   # Orange 
    STOPED   = ("Stopped", "#FF9800")    # Deep Orange
    FAILED   = ("Failed", "#FF4500")      # Red Orange
    ERROR     = ("Error", "#F44336")      # Red 
    TIMEOUT = ("Timeout", "#FF4081")      # Pink
    
#endregion

#region Core Components
class CellManager(QObject):
    finished = pyqtSignal(bool)
    """Business logic handler for tree items"""
    def __init__(self, identifier, times=3):
        super().__init__()
        self.id = identifier
        self.task_count = 0
        self._mutex = QMutex()

    def execute(self):
        """启动任务的三步验证"""
        with QMutexLocker(self._mutex):
            self.proc = QProcess()
            self.proc.finished.connect(self._on_finished)
            self.proc.errorOccurred.connect(self._on_error)
            self.proc.readyReadStandardError.connect(self._on_stderr_reday)
            self.proc.readyReadStandardOutput.connect(self._on_stdout_reday)
            self.proc.start("icell_pr", ["-tech=/home/data/sbd.tech"]) 

    def _on_stdout_reday(self):
        """处理标准输出"""
        if self.proc.canReadLine():
            line = self.proc.readLine().data().decode()
            print(f"stdout: {line.strip()}")
    
        
    def stop(self):
        """安全终止进程的三阶段策略"""
        with QMutexLocker(self._mutex):
            print(f"Stopping task {self.id} process state {self.proc.state()}")
            if self.proc.state() == QProcess.NotRunning:
                return False

            # 第一阶段：优雅终止
            print(f"Stopping task {self.id}...")
            self.proc.terminate()
            
            # 设置超时检测
            QTimer.singleShot(3000, self._kill_if_needed)
            return True

    def _kill_if_needed(self):
        """第二阶段：强制终止"""
        with QMutexLocker(self._mutex):
            if self.proc.state() == QProcess.Running:
                self.proc.kill()
                self.stopped.emit()

    def _on_finished(self, exit_code):
        """处理正常结束"""
        self.finished.emit(exit_code == 0)

    def _on_error(self, error):
        """处理异常情况"""
        print(f"{self.id} runtime error: {error}  {self.proc.errorString()}")
        self.finished.emit(False)
        
    def _on_stderr_reday(self):
        """处理错误输出"""
        line = self.proc.readAllStandardError().data().decode()
        print(f"stderr: {line.strip()}")
        
class Worker(QObject):
    finished = pyqtSignal(bool)
    
    def __init__(self, manager:CellManager):
        super().__init__()
        self.manager = manager
        self.manager.finished.connect(self._on_finished)
    
    def __call__(self):
        self.manager.execute()
    
    def stop(self):
        self.manager.stop()
        
    def _on_finished(self, success):
        if success:
            print(f"Task {self.manager.id} completed successfully.")
        self.finished.emit(success)
        
        
class TaskSignals(QObject):
    status_changed = pyqtSignal(int, tuple)  # (task_id, status)

# class TaskExecutor(QThread):
class TaskExecutor(QObject):
    """Managed task execution unit"""
    def __init__(self, task_id, worker: Worker):
        super().__init__()
        self.task_id  = task_id
        self.worker  = worker
        self.signals  = TaskSignals()
        self._status = None
        self.status = TaskStatus.PENDING
        self.worker.finished.connect(self._on_finished)

    @property
    def status(self):
        return self._status

    @status.setter 
    def status(self, value):
        self._status = value
        self.signals.status_changed.emit(self.task_id, value)

    def run(self):
        """Thread-safe execution logic"""
        try:
            self.status  = TaskStatus.RUNNING
            self.worker()
        except Exception as e:
            print(f"task_id {self.task_id}, runtime error {e}")
            self.status  = TaskStatus.ERROR
            
    def start(self):    
        try:
            self.status  = TaskStatus.RUNNING
            self.worker()
        except Exception as e:
            print(f"task_id {self.task_id}, runtime error {e}")
            self.status  = TaskStatus.ERROR
            
    def _on_finished(self, success):
        """Handle task completion"""
        if success:
            self.status  = TaskStatus.COMPLETED
        else:
            self.status  = TaskStatus.ERROR
    
    def stop(self):
        """Terminate thread execution"""
        self.worker.stop()
        self.status  = TaskStatus.STOPED


class TaskManager(QObject):
    """Central task scheduler"""
    _instance = None
    MAX_CONCURRENT_TASKS = 2

    def __init__(self):
        super().__init__()
        self._running_tasks = {}
        self._finished_tasks = {}
        self._pendding_tasks = deque()
        self._cancel_tasks = {}
        self._task_counter = 0
        self._lock = QMutex()
        
        self._call_backs = {}

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
    
    def _start_task(self, task: TaskExecutor):
        """Begin task execution"""
        if len(self._running_tasks) < self.MAX_CONCURRENT_TASKS:
            self._running_tasks[task.task_id] = task
            task.start()
        else:
            self._enqueue_task(task)            
    
    def _enqueue_task(self, task: TaskExecutor):
        """Queue task for execution"""
        self._pendding_tasks.append(task)
        task.status = TaskStatus.PENDING

    def _remove_if_in_pending(self, task_id):
        """Check if task is in pending state"""
        for task in self._pendding_tasks:
            if task_id == task.task_id:
                self._pendding_tasks.remove(task)
                self._cancel_tasks[task_id] = task
                task.status = TaskStatus.CANCELED
                break            

    def cancel_task(self, task_id):
        """Terminate task execution"""
        with QMutexLocker(self._lock):
            self._remove_if_in_pending(task_id)
                
    def stop_task(self, task_id):
        """Pause task execution"""
        with QMutexLocker(self._lock):
            if task_id in self._running_tasks:
                task = self._running_tasks.pop(task_id)
                task.stop()
                self._cancel_tasks[task_id] = task
                print(f"Task {task_id} stopped")
            else:
                print(f"Task {task_id} not found")
    
    def restart_task(self, task_id):
        """Restart task execution"""
        with QMutexLocker(self._lock):
            if task_id in self._finished_tasks:
                task = self._finished_tasks.pop(task_id)
                self._start_task(task)
            elif task_id in self._cancel_tasks:
                task = self._cancel_tasks.pop(task_id)
                self._start_task(task)
            else:
                print(f"Task {task_id} not found")

    def create_task(self, worker, callback):
        """Register and dispatch new task"""
        with QMutexLocker(self._lock):
            self._task_counter  += 1
            task = TaskExecutor(self._task_counter,  worker)
            self._call_backs[self._task_counter] = callback
            task.signals.status_changed.connect(self.update_status, Qt.ConnectionType.QueuedConnection)
            self._start_task(task)

        return self._task_counter

    def update_status(self, task_id, status):
        """Broadcast status changes"""
        with QMutexLocker(self._lock):
            if task_id in self._call_backs:
                self._call_backs[task_id](task_id, status)
            if status == TaskStatus.COMPLETED or status == TaskStatus.ERROR:
                if task_id in self._running_tasks:
                    self._finished_tasks[task_id] = self._running_tasks.pop(task_id)
                if self._pendding_tasks:
                    self._start_task(self._pendding_tasks.popleft())

    def clean_up(self):
        """Terminate all tasks"""
        with QMutexLocker(self._lock):
            for task in self._running_tasks.values():
                task.stop()
            self._running_tasks.clear()
            self._pendding_tasks.clear()
            self._finished_tasks.clear()
            self._cancel_tasks.clear()
            self._task_counter = 0
            self._call_backs.clear()
#endregion

#region GUI Components
class DynamicControlButton(QWidget):
    """Unified action button with state-driven visualization"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_action = None 
 
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5,  2, 5, 2)
        self.btn  = QPushButton()
        self.btn.setFlat(True) 
        self.btn.setCursor(Qt.PointingHandCursor) 
        layout.addWidget(self.btn) 
        
        # Hover animation 
        # self._anim = qta.IconWidgetAnim(self.btn) 
        # self.btn.installEventFilter(self) 
 
    def set_action(self, status: TaskStatus):
        """Update visual presentation based on task state"""
        if status == TaskStatus.PENDING:
            self.btn.setIcon(qta.icon("mdi.close",  color="#FF1744"))
            self.btn.setToolTip("Cancel  this pending task")
            self._current_action = "cancel"
        elif status == TaskStatus.RUNNING:
            self.btn.setIcon(qta.icon("mdi.stop",  color="#F50057"))
            self.btn.setToolTip("Stop  running task immediately")
            self._current_action = "stop"
        else:
            self.btn.setIcon(qta.icon("mdi.restart",  color="#2962FF"))
            self.btn.setToolTip("Restart  completed/canceled/errored task")
            self._current_action = "restart"
 
        # self._anim.start(scale_factor=1.2,  duration=300)
 
# ============================ Task Monitor ==============================
class TaskMonitor(QTableWidget):
    """Real-time task status dashboard"""
    COLUMNS = ["ID", "Status", "Type", "Details", "Start Time", "End Time", "Duration", "Control"]
    control_clicked = pyqtSignal(int, str)  # (task_id, action_type)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.verticalHeader().setDefaultSectionSize(24)
        self._lock = QMutex()

    def _init_ui(self):
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def update_entry(self, task_id, status, type="Place & Route", details=""):
        """Update or create task row"""
        with QMutexLocker(self._lock):
            row = self._find_row(task_id)
            if row is None:
                row = self._create_row(task_id)
            self._update_cells(task_id, row, status, type, details=f"{type}: {details}")

    def _find_row(self, task_id):
        items = self.findItems(str(task_id), Qt.MatchExactly)
        return items[0].row() if items else None

    def _create_row(self, task_id):
        row = self.rowCount()
        self.insertRow(row)
        self.setItem(row, 0, QTableWidgetItem(str(task_id)))
        for col in range(1, self.columnCount()):
            self.setItem(row, col, QTableWidgetItem())
        return row

    def _update_time(self, row, status):
        if status == TaskStatus.PENDING:
            return
        if status == TaskStatus.RUNNING:
            self.setItem(row, 4, QTableWidgetItem(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")))
            # self.item(row, 4).setText(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
        else:
            start_time = QDateTime.fromString(self.item(row, 4).text(), "yyyy-MM-dd hh:mm:ss")
            end_time = QDateTime.currentDateTime()
            self.item(row, 5).setText(end_time.toString("yyyy-MM-dd hh:mm:ss"))
            self.item(row, 6).setText(f"{start_time.secsTo(end_time)}s")

    def _update_cells(self, task_id, row, status, type, details):
        status_item = self.item(row, 1)
        status_item.setText(status[0])
        status_item.setBackground(QColor(status[1]))
        self.item(row, 2).setText(type)
        self.item(row, 3).setText(str(details)[:50])
        self._update_time(row, status)
        self._update_control_button(task_id, row, status)
        
    def _update_control_button(self, task_id, row, status):
        control = self.cellWidget(row, 7)
        if control is None:
            control = DynamicControlButton()
            self.setCellWidget(row, 7, control)
        control.btn.clicked.connect( 
            lambda: self.control_clicked.emit(task_id, control._current_action))
        control.set_action(status)


class MainWindow(QMainWindow):
    """Main application window with simplified tree structure"""
    def __init__(self):
        super().__init__()
        self.task_manager: TaskManager = TaskManager.instance() 
        self._managers = {}
        self._init_ui()
        self._setup_tree()
        self._connect_signals()
 
    def _init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("Task  Manager - 2025-02-28")
        self.resize(1024,  768)
        
        # Create toolbar with run button 
        toolbar = self.addToolBar("Control") 
        self.run_btn = QAction(qta.icon('msc.play'), "Run", self)
        toolbar.addAction(self.run_btn) 
 
        # Configure tree widget 
        self.tree  = QTreeWidget()
        self.tree.setHeaderLabel("Project  Structure")
        self.tree.setStyle(QStyleFactory.create("Fusion")) 
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection) 
 
        # Setup monitoring panel 
        self.monitor  = TaskMonitor()
        self.monitor.control_clicked.connect(self.control_task)
        dock = QDockWidget("Runtime Monitor", self)
        dock.setWidget(self.monitor) 
        self.addDockWidget(Qt.BottomDockWidgetArea,  dock)
        
        self.setCentralWidget(self.tree) 
        
    def _setup_tree(self):
        """Build simplified tree structure without checkboxes"""
        modules = [
            ("AI Processor", ["Neural Core", "Tensor Unit", "Memory Controller"]),
            ("Sensor Hub", ["Vision Module", "Motion Detect", "Env Sensor"]),
            ("Comm Module", ["5G Modem", "WiFi 7", "Bluetooth 6"])
        ]
        
        for parent_text, children in modules:
            parent = QTreeWidgetItem(self.tree,  [parent_text])
            parent.setFlags(parent.flags()  | Qt.ItemIsAutoTristate)
            for child_text in children:
                child = QTreeWidgetItem(parent, [child_text])
                self._bind_manager(child.text(0))
        
    def control_task(self, task_id, action):
        """Handle task control actions"""
        print(f"Control task {task_id} with action: {action}")  
        if action == "cancel":
            self.task_manager.cancel_task(task_id)
        elif action == "stop":
            self.task_manager.stop_task(task_id)
        elif action == "restart":
            self.task_manager.restart_task(task_id)
 
 
    def _bind_manager(self, identifier):
        """Attach business logic to tree items"""
        manager = CellManager(identifier)
        self._managers[identifier] = manager
 
    def _connect_signals(self):
        """Establish signal connections"""
        self.run_btn.triggered.connect(self._on_execute_clicked) 
        
    def run_task(self, manager):
        manager.execute()
        return manager.result()
 
    def _on_execute_clicked(self):
        """Handle execution trigger for selected items"""
        try:
            selected_items = self.tree.selectedItems() 
            for item in selected_items:
                manager = self._managers.get(item.text(0))
                if manager:
                    worker = Worker(manager)
                    self._start_processing(item, worker)
                else:
                    print(f"Manager not found for {item.text(0)}")
        except Exception as e:
            print(e)
 
    def _start_processing(self, item, worker):
        """Initiate task processing"""
        task_id = self.task_manager.create_task(worker, lambda tid, status: self._on_task_complete(tid, status, item))
        # self.monitor.update_entry(task_id, TaskStatus.PENDING)
         
    def _on_task_complete(self, task_id, status, item):
        """Handle task completion"""
        self.monitor.update_entry(task_id, status, details=item.text(0))
        
    def closeEvent(self, a0):
        self.task_manager.clean_up()
        return super().closeEvent(a0)

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    app.setStyle("Fusion") 
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_()) 
    