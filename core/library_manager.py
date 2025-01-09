import os, json
import pacpy
from .observe import Subject
from .setting_manager import setting_manager, SettingManager
from backend.lef_parser import LefDscp, parse_lef_file
from .pin_destiny import calc_pin_density

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
            self.pac_rule = {}
            
            self.lef_dscp: LefDscp = None
            self.def_dscp = None
            self.gds = None
            self.netlist = None
        
    def change_value(self):
        self.notify()

    def load_lef_file(self, lef_file):
        self.lef_file = lef_file
        self.lef_dscp = parse_lef_file(lef_file)
        self.change_value()
    
    def _get_base_pac_input(self):
        self.pac_rule = setting_manager().get_pac_rule()
        
        lef_file = self.lef_file
        base_name = os.path.basename(lef_file)
        path = os.path.dirname(lef_file)
        
        min_width = self.pac_rule.get('min_width', 0.6)
        s = {"lefFiles": base_name, "min_width": min_width, "path": path}
        return s
    
    def calc_macro_score(self, macro_name=None):
        base_input = self._get_base_pac_input()
        
        score = pacpy.calc_macro_score(json.dumps(base_input))
        macro_scores = json.loads(score)
        return macro_scores.get(macro_name, None) if macro_name else macro_scores
    
    def calc_pin_score(self, macro_name=None):        
        base_input = self._get_base_pac_input()    
            
        base_input["min_space"] = self.pac_rule.get('min_space', 0.6)
        base_input["expand"] = self.pac_rule.get('expand', True)
        score = pacpy.calc_pin_score(json.dumps(base_input))
        pin_scores = json.loads(score)
        return pin_scores.get(macro_name, {}) if macro_name else pin_scores

    def calc_pin_density(self, macro_name=None):
        return calc_pin_density(self.lef_dscp.macros, macro_name) if self.lef_dscp else {}
            
    def load_def_file(self, def_file):
        pass
    
    def load_gds_file(self, gds_file):
        pass
    
    def load_spice_file(self, sp_file):
        pass

    def get_all_macros(self):
        return self.lef_dscp.macros.keys() if self.lef_dscp else []
    
    def get_macro_info(self, name):
        return self.lef_dscp.macro_info(name)
    
    @staticmethod
    def get_instance():
        """Static method to get the single instance of LibraryManager"""
        if LibraryManager._instance is None:
            LibraryManager()  # Creates the instance if it doesn't exist
        return LibraryManager._instance


def library_manager() -> LibraryManager:
    """Helper funtion to get LibraryManager inst"""
    return LibraryManager.get_instance()
