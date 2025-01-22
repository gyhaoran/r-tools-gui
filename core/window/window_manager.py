
class WindowManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ method to implement Singleton pattern"""
        if cls._instance is None:
            # If no instance exists, create one and store it
            cls._instance = super(WindowManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the window manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.windows = {}

    def add_window(self, win_id: str, window):
        """Add sub-windows for mainwindow"""
        if win_id in self.windows:
            return
        self.windows[win_id] = window
        
    def get_window(self, win_id: str):
        """get sub-window in mainwindow"""
        return self.windows.get(win_id, None)
    
    def show_all_windows(self, mainwindow):
        """Show all windows in mainwindow"""
        for _, window in self.windows.items():
            if window.is_center():
                mainwindow.setCentralWidget(window.widget())
                mainwindow.setContentsMargins(0, 0, 0, 0)
            else:
                mainwindow.addDockWidget(window.area(), window.widget())
    
    def print(self, mainwindow):
        for win_id, window in self.windows.items():
            print(win_id, ": ", mainwindow.dockWidgetArea(window.widget()))

    @staticmethod
    def get_instance():
        """Static method to get the single instance of WindowManager"""
        if WindowManager._instance is None:
            WindowManager() # Creates the instance if it doesn't exist
        return WindowManager._instance


def window_manager() -> WindowManager:
    """Helper funtion to get WindowManager inst"""
    return WindowManager.get_instance()
