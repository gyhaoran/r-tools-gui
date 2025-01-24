from .setting_manager import setting_manager, SettingManager


class SettingPageRegistor():
    def __init__(self, page_id):
        """Initialize the setting page manager"""
        setting_manager().add_page(page_id, self)
