
class SettingPageManager():
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ method to implement Singleton pattern"""
        if cls._instance is None:
            # If no instance exists, create one and store it
            cls._instance = super(SettingPageManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the setting page manager"""
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
            self._pages = {}

    def add_page(self, page_id, page):
        self._pages[page_id] = page

    def add_pages(self, pages):
        self._pages.update(pages)

    def get_pages(self, page_id):
        return self._pages.get(page_id, None)

    @staticmethod
    def get_instance():
        """Static method to get the single instance of SettingPageManager"""
        if SettingPageManager._instance is None:
            SettingPageManager()  # Creates the instance if it doesn't exist
        return SettingPageManager._instance

def setting_page_manager() -> SettingPageManager:
    """Helper funtion to get SettingPageManager inst"""
    return SettingPageManager.get_instance()
