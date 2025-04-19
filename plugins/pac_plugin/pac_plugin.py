from .pac_window import PacWindow

class PacPlugin:
    def __init__(self, main_window):
        self.pac_win = PacWindow(main_window)
        self._desc = {
            "name": "PacPlugin",
            "version": "0.0.9",
            "vendor": "iCell",
            "description": "PAC Tools plugin, for pin assessment.",
            "dependencies": ["CorePlugin"],
            "loaded": True,
        }

    def load(self):
        self._desc['loaded'] = True

    def unload(self):
        self._desc['loaded'] = False
    
    def is_load(self):
        return self._desc['loaded']
    
    def name(self):
        return self._desc['name']
    
    def version(self):
        return self._desc['version']
    
    def desc(self):
        return self._desc['description']
    
    def vendor(self):
        return self._desc['vendor']
