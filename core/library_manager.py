import os, json
import pacpy
from backend.lef_parser import LefDscp, parse_lef_file
from .observe import Subject


class LibraryManager(Subject):
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Override __new__ method to implement Singleton pattern"""
        if cls._instance is None:
            # If no instance exists, create one and store it
            cls._instance = super(LibraryManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize the library manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
        super().__init__()
        
        self.lef_file = ''
        
        self.lef_dscp: LefDscp = None
        self.def_dscp = None
        self.gds = None
        self.netlist = None
        
        self.macro_scores = {}
        self.pin_scores = {}
        
    def change_value(self):
        self.notify()

    def load_lef_file(self, lef_file):
        self.lef_file = lef_file
        self.lef_dscp = parse_lef_file(lef_file)
        self.change_value()
    
    def _get_base_pac_input(self):
        lef_file = self.lef_file
        base_name = os.path.basename(lef_file)
        path = os.path.dirname(lef_file)
        s = {"lefFiles": base_name, "min_width":0.06, "path": path}
        return s
    
    def calc_macro_score(self, macro_name):
        base_input = self._get_base_pac_input()
        score = pacpy.calc_macro_score(json.dumps(base_input))
        self.macro_scores = json.loads(score)
        return self.macro_scores.get(macro_name, None)        
    
    def calc_pin_score(self, macro_name):
        base_input = self._get_base_pac_input()
        base_input["min_space"] = 0.06
        score = pacpy.calc_pin_score(json.dumps(base_input))
        self.pin_scores = json.loads(score)
        return self.pin_scores.get(macro_name, {})
        
    def load_def_file(self, def_file):
        pass
    
    def load_gds_file(self, gds_file):
        pass
    
    def load_sp_file(self, sp_file):
        pass

    def get_all_macros(self):
        return self.lef_dscp.macros.keys() if self.lef_dscp else []
    
    @staticmethod
    def get_instance():
        """Static method to get the single instance of LibraryManager"""
        if LibraryManager._instance is None:
            LibraryManager()  # Creates the instance if it doesn't exist
        return LibraryManager._instance


def library_manager() -> LibraryManager:
    """Helper funtion to get LibraryManager inst"""
    return LibraryManager.get_instance()
