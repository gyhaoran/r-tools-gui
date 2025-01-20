import importlib
import os

class PluginManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins = []

    def load_plugins(self):
        """Load CorePlugin first, then load all non-core plugins."""
        # Load CorePlugin
        self._load_plugin("core_plugin", True)

        # Load non-core plugins
        plugins_dir = os.path.dirname(__file__)
        for plugin_name in os.listdir(plugins_dir):
            if plugin_name == "core_plugin" or plugin_name == "__pycache__" or \
                not os.path.isdir(os.path.join(plugins_dir, plugin_name)):
                continue  # Skip core_plugin and non-directory files
            self._load_plugin(plugin_name, True)


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
            self.plugins.append(plugin_instance)
            # print(f"Plugin {plugin_name} loaded successfully.")
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")

    def unload_plugins(self):
        """Unload all plugins."""
        for plugin in self.plugins:
            plugin.unload()
            print(f"Plugin {plugin.__class__.__name__} unloaded.")
        self.plugins.clear()
