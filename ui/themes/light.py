# -*- coding: utf-8 -*-

"""QDarkStyle default light palette."""

# Local imports
from .colorsystem import Blue, Gray
from qdarkstyle.palette import Palette


class CmosLightPalette(Palette):
    """Theme variables."""

    ID = 'light'

    # Color
    COLOR_BACKGROUND_1 = Gray.B140
    COLOR_BACKGROUND_2 = Gray.B140
    COLOR_BACKGROUND_3 = Gray.B140
    COLOR_BACKGROUND_4 = Gray.B140
    COLOR_BACKGROUND_5 = Gray.B140
    COLOR_BACKGROUND_6 = Gray.B140

    COLOR_TEXT_1 = Gray.B10
    COLOR_TEXT_2 = Gray.B20
    COLOR_TEXT_3 = Gray.B50
    COLOR_TEXT_4 = Gray.B0

    COLOR_ACCENT_1 = Blue.B130
    COLOR_ACCENT_2 = Blue.B100
    COLOR_ACCENT_3 = Blue.B90
    COLOR_ACCENT_4 = Blue.B80
    COLOR_ACCENT_5 = Blue.B70
    
    # Color for disabled elements
    COLOR_DISABLED = Gray.B0

    OPACITY_TOOLTIP = 230
