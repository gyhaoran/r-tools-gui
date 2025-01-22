from ui.widgets import (
    LibBrowserWindow,
    LefMacroWindow,
    PinAssessWindow
)


def register_windows(main_window):
    macro_win = LefMacroWindow(main_window)
    pin_assess_win = PinAssessWindow(main_window)    
    lib_browser_win = LibBrowserWindow(macro_win, pin_assess_win, main_window)
    