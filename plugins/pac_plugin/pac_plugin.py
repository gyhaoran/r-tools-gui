import json
import os
from .ui import *
from core.window import *
from ui.icons import *

class PacPlugin:
    def __init__(self, main_window):
        self.main_window = main_window        
        config_file = os.path.join(os.path.dirname(__file__), 'pac_plugin.json')
        self.descp = self._read_plugin_config(config_file)
        self._register_windows(main_window)        
        self._setup_ui(main_window)
        
    def _setup_ui(self, main_window):
        tools_menu = menu_manager().get_menu(M_TOOLS_ID)        
        pin_rule_action = main_window.create_action('Pin Assess Rule', M_TOOLS_PIN_RULE_ICON, lambda: main_window.show_settings(1))
        drc_rule_action = main_window.create_action('Drc Rule', M_TOOLS_DRC_RULE_ICON, lambda: main_window.show_settings(2))
        tools_menu.addActions([pin_rule_action, drc_rule_action])
        tools_menu.addSeparator()
        
        pin_assess_action = main_window.create_action('PinAssess', M_TOOLS_PIN_ASSESS_ICON, main_window.assess_pin)
        macro_assess_action = main_window.create_action('MacroAssess', M_TOOLS_MACRO_COST_ICON, main_window.assess_macro)
        pin_density_action = main_window.create_action('PinDensity', M_TOOLS_PIN_DENSITY_ICON, main_window.assess_pin_density)
        
        tool_actions = [pin_assess_action, macro_assess_action, pin_density_action]
        tools_menu.addActions(tool_actions)        
        tool_actions.append(pin_rule_action)
        toolbar_manager().add_actions(TOOLBAR_TOOLS, tool_actions)

    def _read_plugin_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as fin:
            descp = json.loads(fin.read())
        return descp

    def _register_windows(self, main_window):
        macro_win = LefMacroWindow(main_window)
        pin_assess_win = PinAssessWindow(main_window)    
        LibBrowserWindow(macro_win, pin_assess_win, main_window)        

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
