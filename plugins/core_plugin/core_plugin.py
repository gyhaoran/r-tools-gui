
class CorePlugin:
    def __init__(self, main_window):
        self.main_window = main_window
        self._desc = {
            "name": "CorePlugin",
            "version": "0.1.0",
            "vendor": "iCell",
            "description": "The core plugin for the iCell IDE.",
            "dependencies": [],
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
