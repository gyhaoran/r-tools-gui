import os


class SettingManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ method to implement Singleton pattern"""
        if cls._instance is None:
            # If no instance exists, create one and store it
            cls._instance = super(SettingManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the action manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.actions = {}

        self.general_setting = {}
        self.pac_rule_setting = {}
        self.drc_rule_setting = {}
    
    def get_pac_rule(self):
        return self.pac_rule_setting
    
    def get_drc_rule(self):
        return self.drc_rule_setting
    
    def update_settings(self, general, pac, drc):
        self.general_setting = general
        self.pac_rule_setting = pac
        self.drc_rule_setting = drc

    @staticmethod
    def get_instance():
        """Static method to get the single instance of SettingManager"""
        if SettingManager._instance is None:
            SettingManager()  # Creates the instance if it doesn't exist
        return SettingManager._instance


def setting_manager() -> SettingManager:
    """Helper funtion to get SettingManager inst"""
    return SettingManager.get_instance()
