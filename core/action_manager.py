
class ActionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ method to implement Singleton pattern"""
        if cls._instance is None:
            # If no instance exists, create one and store it
            cls._instance = super(ActionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the action manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.actions = {}

    def add_action(self, action_id: int, action):
        if action_id not in self.actions:
            self.actions[action_id] = []
        self.actions[action_id].append(action)

    def add_actions(self, action_id: int, actions):
        if action_id not in self.actions:
            self.actions[action_id] = []
        self.actions[action_id].extend(actions)

    def get_action(self, action_id: int):
        return self.actions.get(action_id, [])

    def get_all_actions(self):
        return self.actions

    @staticmethod
    def get_instance():
        """Static method to get the single instance of ActionManager"""
        if ActionManager._instance is None:
            ActionManager()  # Creates the instance if it doesn't exist
        return ActionManager._instance


def action_manager() -> ActionManager:
    """Helper funtion to get ActionManager inst"""
    return ActionManager.get_instance()
