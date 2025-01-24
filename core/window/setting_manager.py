import os
import json
from pathlib import Path

def get_user_home_dir():
    return str(Path.home())

class SettingManager():
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
            self._all_settings = {}
            self._load_settings() 
            self._pages = {}

    def add_page(self, page_id, page):
        self._pages[page_id] = page

    def add_pages(self, pages):
        self._pages.update(pages)

    def get_pages(self):
        return self._pages

    @property
    def config_path(self):
        home_dir = get_user_home_dir()
        return os.path.join(home_dir, self._config_dir, self._config_file)

    def _load_last_settings(self, config_path):
        """Load last settings from a JSON file."""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._all_settings = json.load(f)

    def _load_settings(self):
        """Load settings from a JSON file."""
        config_path = self.config_path
        config_dir = os.path.dirname(config_path)
        os.makedirs(config_dir, exist_ok=True) # Ensure the directory exists        
        self._load_last_settings(config_path)        

    def save(self):
        for _, page in self._pages.items():
            page.save()

    def update_settings(self):
        for _, page in self._pages.items():
            self._all_settings.update(page.get_setting())        

    def save_settings(self):
        """Save current settings to a JSON file."""
        self.update_settings()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._all_settings, f, indent=2)       
            
    def has_modified(self)-> bool:
        return any(page.has_modified() for _, page in self._pages.items())
    
    def get_pac_rule(self):
        """Get current pac setting"""
        return self._all_settings.get(self._all_settings['pac'], {})
    
    def get_drc_rule(self):
        """Get current drc setting"""
        return self._all_settings.get(self._all_settings['drc'], {})

    @staticmethod
    def get_instance():
        """Static method to get the single instance of SettingManager"""
        if SettingManager._instance is None:
            SettingManager()  # Creates the instance if it doesn't exist
        return SettingManager._instance


def setting_manager() -> SettingManager:
    """Helper funtion to get SettingManager inst"""
    return SettingManager.get_instance()
