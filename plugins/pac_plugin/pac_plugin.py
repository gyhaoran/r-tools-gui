import json
import os
from .pac_window import PacWindow

class PacPlugin:
    def __init__(self, main_window):
        self.pac_win = PacWindow(main_window)
        config_file = os.path.join(os.path.dirname(__file__), 'pac_plugin.json')
        self.descp = self._read_plugin_config(config_file)

    def _read_plugin_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as fin:
            descp = json.loads(fin.read())
        return descp

    def load(self):
        self.descp['loaded'] = True

    def unload(self):
        self.descp['loaded'] = False
    
    def is_load(self):
        return self.descp['loaded']
    
    def name(self):
        return self.descp['name']
    
    def version(self):
        return self.descp['version']
    
    def desp(self):
        return self.descp['description']
    
    def vendor(self):
        return self.descp['vendor']
