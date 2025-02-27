import sys
import random
from PyQt5.QtCore import (Qt, QObject, QRunnable, pyqtSignal, pyqtSlot,
                         QThreadPool, QTimer)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidget,
                             QTreeWidgetItem, QDockWidget, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget,
                             QHeaderView, QStyleFactory)

#region Constants and Enums
class TaskStatus:
    PENDING = ("Pending", "#FFD700")    # Gold
    RUNNING = ("Running", "#1E90FF")    # Dodger Blue
    COMPLETED = ("Completed", "#32CD32")# Lime Green
    ERROR = ("Error", "#FF4500")        # Orange Red

class DataRole:
    CELL_MANAGER = Qt.UserRole + 1
    TASK_HISTORY = Qt.UserRole + 2
#endregion

#region Core Components
class CellManager(QObject):
    """Business logic handler for tree items"""
    def __init__(self, identifier):
        super().__init__()
        self.id  = identifier
        self.task_count  = 0

    def execute(self):
        """Simulate task execution with random results"""
        try:
            if random.random()  < 0.2:  # 20% error rate
                raise RuntimeError("Simulated execution error")

            delay = random.uniform(0.5,  3.0)
            results = random.randint(1,  5)
            return (delay, results)
        except Exception as e:
            return (0, str(e))

class TaskSignals(QObject):
    status_changed = pyqtSignal(int, tuple)  # (task_id, status)
    result_ready = pyqtSignal(int, object)   # (task_id, result)

class TaskExecutor(QRunnable):
    """Managed task execution unit"""
    def __init__(self, task_id, manager):
        super().__init__()
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
        self.signals.status_changed.emit(self.task_id,  value)

    @pyqtSlot()
    def run(self):
        """Thread-safe execution logic"""
        try:
            self.status  = TaskStatus.RUNNING
            result = self.manager.execute() 
            
            if isinstance(result[1], Exception):
                raise result[1]
                
            self.signals.result_ready.emit(self.task_id,  result)
            self.status  = TaskStatus.COMPLETED
        except Exception as e:
            self.status  = TaskStatus.ERROR
            self.signals.result_ready.emit(self.task_id,  (0, str(e)))

class TaskController(QObject):
    """Central task scheduler"""
    _instance = None

    def __init__(self):
        super().__init__()
        self.thread_pool  = QThreadPool.globalInstance() 
        self.tasks  = {}
        self.task_counter  = 0

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def create_task(self, manager, callback):
        """Register and dispatch new task"""
        self.task_counter  += 1
        task = TaskExecutor(self.task_counter,  manager)
        task.signals.result_ready.connect(callback) 
        task.signals.status_changed.connect(self.update_status) 
        self.tasks[self.task_counter]  = task
        self.thread_pool.start(task) 
        return self.task_counter 

    def update_status(self, task_id, status):
        """Broadcast status changes"""
        task = self.tasks.get(task_id) 
        if task:
            task.status  = status
#endregion

#region GUI Components
class TaskMonitor(QTableWidget):
    """Real-time task status dashboard"""
    COLUMNS = ["ID", "Status", "Duration", "Details"]

    def __init__(self):
        super().__init__()
        self._init_ui()
        self.verticalHeader().setDefaultSectionSize(24) 

    def _init_ui(self):
        self.setColumnCount(len(self.COLUMNS)) 
        self.setHorizontalHeaderLabels(self.COLUMNS) 
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.setSelectionMode(QTableWidget.SingleSelection) 
        self.setEditTriggers(QTableWidget.NoEditTriggers) 

    def update_entry(self, task_id, status, duration=0, details=""):
        """Update or create task row"""
        row = self._find_row(task_id) or self._create_row(task_id)
        self._update_cells(row, status, duration, details)

    def _find_row(self, task_id):
        items = self.findItems(str(task_id),  Qt.MatchExactly)
        return items[0].row() if items else None

    def _create_row(self, task_id):
        row = self.rowCount() 
        self.insertRow(row) 
        self.setItem(row,  0, QTableWidgetItem(str(task_id)))
        for col in range(1, self.columnCount()): 
            self.setItem(row,  col, QTableWidgetItem())
        return row

    def _update_cells(self, row, status, duration, details):
        status_item = self.item(row,  1)
        status_item.setText(status[0]) 
        status_item.setBackground(QColor(status[1])) 
        
        self.item(row,  2).setText(f"{duration:.2f}s" if duration else "")
        self.item(row,  3).setText(str(details)[:50])

class MainWindow(QMainWindow):
    """Primary application window"""
    def __init__(self):
        super().__init__()
        self.task_ctrl  = TaskController.instance() 
        self._init_ui()
        self._setup_tree()
        self._connect_signals()

    def _init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("Advanced  Task Manager")
        self.resize(1024,  768)
        
        # Configure tree widget
        self.tree  = QTreeWidget()
        self.tree.setHeaderLabel("Process  Hierarchy")
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection) 
        self.tree.setStyle(QStyleFactory.create("Fusion")) 
        
        # Setup monitoring panel
        self.monitor  = TaskMonitor()
        dock = QDockWidget("Execution Monitor", self)
        dock.setWidget(self.monitor) 
        self.addDockWidget(Qt.BottomDockWidgetArea,  dock)
        
        self.setCentralWidget(self.tree) 

    def _setup_tree(self):
        """Build sample tree structure"""
        for i in range(3):
            parent = QTreeWidgetItem(self.tree,  [f"Root Process {i+1}"])
            for j in range(3):
                child = QTreeWidgetItem(parent, [f"Subtask {i+1}.{j+1}"])
                child.setFlags(child.flags()  | Qt.ItemIsUserCheckable)
                child.setCheckState(0,  Qt.Unchecked)
                self._bind_manager(child, f"proc_{i}_{j}")

    def _bind_manager(self, item, identifier):
        """Attach cell manager to tree item"""
        manager = CellManager(identifier)
        item.setData(0,  DataRole.CELL_MANAGER, manager)
        item.setData(0,  DataRole.TASK_HISTORY, [])

    def _connect_signals(self):
        """Establish UI signal connections"""
        self.tree.itemSelectionChanged.connect(self._handle_selection) 
        self.task_ctrl.task_created.connect(self._log_task) 

    def _handle_selection(self):
        """Process item selection changes"""
        for item in self.tree.selectedItems(): 
            if item.checkState(0)  == Qt.Checked:
                self._start_processing(item)

    def _start_processing(self, item):
        """Initiate task execution"""
        if not (manager := item.data(0,  DataRole.CELL_MANAGER)):
            return

        task_id = self.task_ctrl.create_task( 
            manager,
            lambda tid, res: self._on_task_complete(tid, res, item)
        )
        
        history = item.data(0,  DataRole.TASK_HISTORY)
        history.append({ 
            "id": task_id,
            "timestamp": QDateTime.currentDateTime(), 
            "status": TaskStatus.PENDING
        })
        item.setData(0,  DataRole.TASK_HISTORY, history)

    def _on_task_complete(self, task_id, result, item):
        """Handle task completion callback"""
        duration, output = result
        self.monitor.update_entry(task_id,  TaskStatus.COMPLETED, duration, output)
        
        if isinstance(output, int) and output > 0:
            item.takeChildren() 
            for i in range(output):
                QTreeWidgetItem(item, [f"Result {i+1}"])
        elif isinstance(output, str):
            self._show_error(item, output)

    def _show_error(self, item, message):
        """Display error information"""
        error_item = QTreeWidgetItem(item, ["Execution Failed"])
        error_item.setForeground(0,  QColor(TaskStatus.ERROR[1]))
        error_item.setToolTip(0,  message)
#endregion

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    app.setStyle("Fusion") 
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_()) 