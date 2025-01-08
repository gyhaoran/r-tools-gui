import os
import json
from pathlib import Path

def get_user_home_dir():
    return str(Path.home())

class SettingManager:
    _instance = None
    _config_dir = '.iCellGui'
    _config_file = 'settings.json'

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

            self.general = {}
            self.pac = 'asap7'
            self.drc = 'asap7'
            
            self.pac_rules = {
                "asap7" : {"min_width": 0.06, "min_space": 0.06, "expand": True},
                "smic7" : {"min_width": 0.20, "min_space": 0.20, "expand": False},
                "smic14": {"min_width": 0.30, "min_space": 0.30, "expand": True},
            }
            
            self.drc_rules = {
                "asap7" : {"min_width": 0.06, "min_space": 0.06, "min_contact_size": 0.2},
                "smic7" : {"min_width": 0.02, "min_space": 0.02, "min_contact_size": 0.3},
                "smic14": {"min_width": 0.03, "min_space": 0.03, "min_contact_size": 0.4},
            }
            
            # Load settings when the instance is created for the first time
            self.load_settings() 

    @property
    def config_path(self):
        home_dir = get_user_home_dir()
        return os.path.join(home_dir, self._config_dir, self._config_file)

    def load_settings(self):
        """Load settings from a JSON file."""
        config_path = self.config_path
        config_dir = os.path.dirname(config_path)

        # Ensure the directory exists
        os.makedirs(config_dir, exist_ok=True)

        # Try to load existing settings
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.general = data.get('general', {})
                self.pac = data.get('pac', 'asap7')
                self.drc = data.get('drc', 'asap7')
                self.pac_rules = data.get('pac_rules', self.pac_rules)
                self.drc_rules = data.get('drc_rules', self.drc_rules)

    def save_settings(self):
        """Save current settings to a JSON file."""
        data = {
            'general': self.general,
            'pac': self.pac,
            'drc': self.drc,
            'pac_rules': self.pac_rules,
            'drc_rules': self.drc_rules,
        }

        config_path = self.config_path
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)       
    
    def get_pac_rule(self):
        """Get current pac setting"""
        return self.pac_rules.get(self.pac, {})
    
    def get_drc_rule(self):
        """Get current drc setting"""
        return self.drc_rules.get(self.drc, {})
    
    def update_cur_settings(self, general, pac, drc):
        self.general = general
        self.pac = pac
        self.drc = drc
    
    def update_settings(self, pac_rules, drc_rules):
        self.pac_rules = pac_rules
        self.drc_rules = drc_rules

    @staticmethod
    def get_instance():
        """Static method to get the single instance of SettingManager"""
        if SettingManager._instance is None:
            SettingManager()  # Creates the instance if it doesn't exist
        return SettingManager._instance


def setting_manager() -> SettingManager:
    """Helper funtion to get SettingManager inst"""
    return SettingManager.get_instance()
