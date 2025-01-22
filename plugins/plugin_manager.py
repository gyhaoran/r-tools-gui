import importlib
import os

class PluginManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins = {}
        self.plugins_path = os.path.dirname(__file__)        

    def load_plugins(self):
        """Load all plugins"""
        for plugin_name in os.listdir(self.plugins_path):
            if self._is_plugin(plugin_name):
                self._load_plugin(plugin_name, True)

    def _is_plugin(self, plugin_name) -> bool:
        return os.path.isdir(os.path.join(self.plugins_path, plugin_name)) and plugin_name != "__pycache__"

    def _load_plugin(self, plugin_name, pass_main_window=False):
        """Load a plugin by name.        
        Args:
            plugin_name (str): The name of the plugin directory.
            pass_main_window (bool): Whether to pass main_window to the plugin.
        """
        try:
            module = importlib.import_module(f"plugins.{plugin_name}.{plugin_name}")
            plugin_class = getattr(module, plugin_name.title().replace("_", ""))
            
            # Pass main_window only if required
            plugin_instance = plugin_class(self.main_window) if pass_main_window else plugin_class()
            plugin_instance.load()
            self.plugins[plugin_instance.name()] = plugin_instance
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")

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
