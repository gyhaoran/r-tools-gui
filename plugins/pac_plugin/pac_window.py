
from .ui import *
from .ui.dialogs import *
from core.window import *
from core import library_manager, LibraryManager
from ui.icons import *


class PacWindow():
    """Pac plugin main window"""
    def __init__(self, main_window):
        self.main_window = main_window
        self._register_windows(main_window)        
        self._setup_ui(main_window)
        main_window.theme_changed.connect(self.change_theme)
    
    def change_theme(self, is_dark):
        self.macro_win.set_theme(is_dark)
        
    def show_lib_browser(self):
        self._show_widgets(self.lib_browser_win.widget())

    def show_macro_view(self):
        self._show_widgets(self.macro_win.widget())
    
    def show_pin_assess_win(self):
        self._show_widgets(self.pin_assess_win.widget())

    def assess_pin(self):
        data = library_manager().calc_pin_score(None)
        dialog = PinScoreDialog(data, self.main_window)
        dialog.exec_()

    def assess_macro(self):
        data = library_manager().calc_macro_score(None)
        dialog = MacroScoreDialog(data, self.main_window)
        dialog.exec_()

    def assess_pin_density(self):
        data = library_manager().calc_pin_density(None)
        dialog = PinDestinyDialog(data, self.main_window)
        dialog.exec_()

    def _create_view_menu(self, main_window):
        view_menu = menu_manager().get_menu(M_VIEW_ID)
        show_lib_action = main_window.create_checked_action('Library', M_VIEW_LIBRARY_ICON, self.show_lib_browser)
        show_macro_action = main_window.create_checked_action('Macro View', M_VIEW_MACRO_VIEW_ICON, self.show_macro_view)
        show_pin_score_action = main_window.create_checked_action('Pin Assess', M_VIEW_PIN_ASSESS_ICON, self.show_pin_assess_win)        
        
        view_actions = [show_lib_action, show_macro_action, show_pin_score_action]
        view_menu.addActions(view_actions)
        view_menu.addSeparator()
        toolbar_manager().add_actions(TOOLBAR_VIEW, view_actions)

    def _create_tools_menu(self, main_window):
        tools_menu = menu_manager().get_menu(M_TOOLS_ID)        
        pin_rule_action = main_window.create_action('Pin Assess Rule', M_TOOLS_PIN_RULE_ICON, lambda: main_window.show_settings(1))
        drc_rule_action = main_window.create_action('Drc Rule', M_TOOLS_DRC_RULE_ICON, lambda: main_window.show_settings(2))
        tools_menu.addActions([pin_rule_action, drc_rule_action])
        tools_menu.addSeparator()
        
        pin_assess_action = main_window.create_action('PinAssess', M_TOOLS_PIN_ASSESS_ICON, self.assess_pin)
        macro_assess_action = main_window.create_action('MacroAssess', M_TOOLS_MACRO_COST_ICON, self.assess_macro)
        pin_density_action = main_window.create_action('PinDensity', M_TOOLS_PIN_DENSITY_ICON, self.assess_pin_density)
        
        tool_actions = [pin_assess_action, macro_assess_action, pin_density_action]
        tools_menu.addActions(tool_actions)
        tool_actions.append(pin_rule_action)
        toolbar_manager().add_actions(TOOLBAR_TOOLS, tool_actions)
        
    def _setup_ui(self, main_window):
        self._create_view_menu(main_window)
        self._create_tools_menu(main_window)

    def _register_windows(self, main_window):
        self.macro_win = LefMacroWindow(main_window)
        self.pin_assess_win = PinAssessWindow(main_window)    
        self.lib_browser_win = LibBrowserWindow(self.macro_win, self.pin_assess_win, main_window)
        self.pin_rule_tab = PinAssessRulePage(setting_manager()._all_settings, main_window)
        self.drc_rule_tab = DrcRulePage(setting_manager()._all_settings, main_window)

    def _show_widgets(self, widget):
        if widget is None:
            return
        if widget.isHidden():
            widget.show()
        else:
            widget.hide()