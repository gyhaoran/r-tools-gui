import os
from .core_plugin import CorePlugin
from .pac_plugin import PacPlugin


class PluginManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins = {}
        self.plugins_path = os.path.dirname(__file__)        

    def load_plugins(self):
        """Load all plugins"""
        try:
            self.plugins.clear()
            self.load_core_plugin()
            self.load_pac_plugin()
        except Exception as e:
            print(f"Failed to load plugin: {e}")

    def load_pac_plugin(self):
        """Load pac plugin"""
        pac_plugin = PacPlugin(self.main_window)
        pac_plugin.load()
        self.plugins[pac_plugin.name()] = pac_plugin
                
    def load_core_plugin(self):
        """Load core plugin"""
        core_plugin = CorePlugin(self.main_window)
        core_plugin.load()
        self.plugins[core_plugin.name()] = core_plugin

    def unload_plugin(self, plugin_name):
        """Unload a specfic plugin."""
        plugin = self.plugins.pop(plugin_name, None)
        if plugin:
            plugin.unload()

    def unload_plugins(self):
        """Unload all plugins."""
        for _, plugin in self.plugins.items():
            plugin.unload()
        self.plugins.clear()
