from .menu_id import *

class MenuManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ method to implement Singleton pattern"""
        if cls._instance is None:
            # If no instance exists, create one and store it
            cls._instance = super(MenuManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, menu_bar):
        """Initialize the menu manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.menus = {}
            self.menu_bar = menu_bar

    def add_menu(self, menu_id: str, menu):
        """Add menu to menubar of mainwindow"""
        if menu_id in self.menus:
            return
        self.menus[menu_id] = menu
        self.menu_bar.addMenu(menu)
    
    def get_menu(self, menu_id: str):
        """Get the menu from mainwindow"""
        return self.menus.get(menu_id, None)

    @staticmethod
    def get_instance():
        """Static method to get the single instance of MenuManager"""
        if MenuManager._instance is None:
            raise RuntimeError("Please create munu manager before use it")
        return MenuManager._instance


def create_menu_manager(menu_bar):
    """Helper function to create MenuManager inst"""
    return MenuManager(menu_bar)


def menu_manager() -> MenuManager:
    """Helper funtion to get MenuManager inst"""
    return MenuManager.get_instance()
