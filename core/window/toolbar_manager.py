from core.observe import Subject


class ToolBarManager(Subject):
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ method to implement Singleton pattern"""
        if cls._instance is None:
            # If no instance exists, create one and store it
            cls._instance = super(ToolBarManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the toolbar manager"""
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
            self.action_groups = {}
    
    def _change_value(self):
        self.notify()

    def add_action(self, group_id: str, action):
        if group_id not in self.action_groups:
            self.action_groups[group_id] = []
        self.action_groups[group_id].append(action)
        self._change_value()

    def add_actions(self, group_id: str, actions):
        if group_id not in self.action_groups:
            self.action_groups[group_id] = []
        self.action_groups[group_id].extend(actions)
        self._change_value()

    def get_actions(self, group_id: str):
        return self.action_groups.get(group_id, [])

    @staticmethod
    def get_instance():
        """Static method to get the single instance of ToolBarManager"""
        if ToolBarManager._instance is None:
            ToolBarManager()  # Creates the instance if it doesn't exist
        return ToolBarManager._instance

def toolbar_manager() -> ToolBarManager:
    """Helper funtion to get ToolBarManager inst"""
    return ToolBarManager.get_instance()
