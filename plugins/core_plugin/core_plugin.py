import os
import json


class CorePlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        
        config_file = os.path.join(os.path.dirname(__file__), 'core_plugin.json')
        self.descp = self._read_plugin_config(config_file)
        
    def _read_plugin_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as fin:
            descp = json.loads(fin.read())
        return descp

    def load(self):
        # print(f"CorePlugin loaded, plugin info {self.descp}")
        self.descp['loaded'] = True

    def unload(self):
        # print("CorePlugin unloaded.")
        self.descp['loaded'] = False
    
    def is_load(self):
        return self.descp['loaded']
    