import sys
import time
import random
import qtawesome as qta
from collections import deque
from PyQt5.QtCore import (Qt, QObject, QRunnable, pyqtSignal, pyqtSlot, QMutex, QMutexLocker,
                         QThreadPool, QTimer, QDateTime)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QAction, QHBoxLayout, QPushButton,
                             QTreeWidgetItem, QDockWidget, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget,
                             QHeaderView, QStyleFactory)

#region Constants and Enums
class TaskStatus:
    PENDING = ("Pending", "#FFD700")    # Gold
    RUNNING = ("Running", "#1E90FF")    # Dodger Blue
    COMPLETED = ("Completed", "#32CD32")# Lime Green
    CANCELED  = ("Canceled", "#FF5722")   # Orange 
    ERROR     = ("Error", "#F44336")      # Red 
    
class DataRole:
    CELL_MANAGER = Qt.UserRole + 1
    TASK_HISTORY = Qt.UserRole + 2
#endregion

#region Core Components
class CellManager(QObject):
    """Business logic handler for tree items"""
    def __init__(self, identifier, times=3):
        super().__init__()
        self.id  = identifier
        self.task_count  = 0
        self.times = times
        self.suspended = False

    def _process(self):
        """Simulate task execution with random results"""
        delay = random.uniform(0.5,  3.0)
        results = random.randint(1,  5)
        
        self._delay()   # Simulate processing time
        return f"d={delay:.2f}s, r={results}"
    
    def _delay(self):
        begin = time.time()
        for i in range(1, 80000000):
            s = i+ i
        end = time.time()
        print(f"delay: {end - begin}")

    def execute(self):
        """Simulate task execution with random results"""
        try:
            print(f"Task: {self.id}, run {self.times} times: ")
            while self.task_count < self.times:
                self.task_count += 1
                results = self._process()
                print(f"  {self.task_count}: {results}")
            if random.random()  < 0.2:  # 20% error rate
                raise RuntimeError("Simulated execution error")
        except Exception as e:
            raise e

class TaskSignals(QObject):
    status_changed = pyqtSignal(int, tuple)  # (task_id, status)

class TaskExecutor(QRunnable):
    """Managed task execution unit"""
    def __init__(self, task_id, manager):
        super().__init__()
        self.setAutoDelete(False)
        self.task_id  = task_id
        self.manager  = manager
        self.signals  = TaskSignals()
        self._status = TaskStatus.PENDING

    @property
    def status(self):
        return self._status

    @status.setter 
    def status(self, value):
        self._status = value
        self.signals.status_changed.emit(self.task_id, value)

    @pyqtSlot()
    def run(self):
        """Thread-safe execution logic"""
        try:
            self.status  = TaskStatus.RUNNING
            self.manager.execute()
            self.status  = TaskStatus.COMPLETED
        except Exception as e:
            print(f"error: {e}")
            self.status  = TaskStatus.ERROR

class TaskManager(QObject):
    """Central task scheduler"""
    _instance = None
    MAX_CONCURRENT_TASKS = 2

    def __init__(self):
        super().__init__()
        self.thread_pool  = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(self.MAX_CONCURRENT_TASKS * 5)
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
            self.thread_pool.start(task)
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
            if task_id in self._running_tasks:
                task = self._running_tasks.pop(task_id)
                task.status = TaskStatus.CANCELED
                self._cancel_tasks[task_id] = task
            else:
                self._remove_if_in_pending(task_id)
                
    def stop_task(self, task_id):
        """Pause task execution"""
        with QMutexLocker(self._lock):
            if task_id in self._running_tasks:
                task = self._running_tasks.pop(task_id)
                self._enqueue_task(task)
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

    def create_task(self, manager, callback):
        """Register and dispatch new task"""
        with QMutexLocker(self._lock):
            self._task_counter  += 1
            task = TaskExecutor(self._task_counter,  manager)
            self._call_backs[self._task_counter] = callback
            task.signals.status_changed.connect(self.update_status)
            self._start_task(task)

        return self._task_counter

    def update_status(self, task_id, status):
        """Broadcast status changes"""
        with QMutexLocker(self._lock):
            if task_id in self._call_backs:
                self._call_backs[task_id](task_id, status)
            if status == TaskStatus.COMPLETED or status == TaskStatus.ERROR:
                self._finished_tasks[task_id] = self._running_tasks.pop(task_id)
                if self._pendding_tasks:
                    self._start_task(self._pendding_tasks.popleft())

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
            self._update_cells(task_id, row, status, type, details)

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
            print("Start Time", row)
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
        
    def control_task(self, task_id, action):
        """Handle task control actions"""
        if action == "cancel":
            self.task_manager.cancel_task(task_id)
        elif action == "stop":
            self.task_manager.stop_task(task_id)
        elif action == "restart":
            self.task_manager.restart_task(task_id)
 
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
 
    def _bind_manager(self, identifier):
        """Attach business logic to tree items"""
        manager = CellManager(identifier)
        self._managers[identifier] = manager
 
    def _connect_signals(self):
        """Establish signal connections"""
        self.run_btn.triggered.connect(self._on_execute_clicked) 
 
    def _on_execute_clicked(self):
        """Handle execution trigger for selected items"""
        try:
            selected_items = self.tree.selectedItems() 
            for item in selected_items:
                manager = self._managers.get(item.text(0))
                if manager:
                    self._start_processing(item, manager)
        except Exception as e:
            print(e)
 
    def _start_processing(self, item, manager):
        """Initiate task processing"""
        task_id = self.task_manager.create_task( 
            manager,
            lambda tid, status: self._on_task_complete(tid, status, item)
        )
         
    def _on_task_complete(self, task_id, status, item):
        """Handle task completion"""
        self.monitor.update_entry(task_id, status)

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    app.setStyle("Fusion") 
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_()) 
    