# R-Tools GUI

## Open Ability Interface
ID   | Funtions                  | Priority |   Status  
---  | -------------             | ----     |    ----    
1    | Plugin Manager            | High     |    Done 
2    | Menu Manager              | High     |    In Progress(90%)
3    | Window Manager            | High     |    In Progress(90%)
4    | ToolBar Manager           | High     |    In Progress(90%)
5    | Settings Manager          | Medium   |    In Progress(90%)
6    | Open Project Interface    | Medium   |    Pending
7    | Plugin View Manager       | Medium   |    Pending
8    | Center Widget Manager     | Lower    |    Pending



## Code Metrics
Date  |  Total nloc  |  Avg.NLOC  |  Avg.CCN |  Version
---   |  ---         |  ---       |  ---     |  ---
1-10  |  1680        |  6.0       |  1.4     |  0.0.1-alpaha
1-24  |  2117        |  4.9       |  1.4     |  0.0.1


pyqt5 gui应用， cmos后端物理设计， 版图自动化工具，布局布线领域

现状：
我现在使用了第三方库qdarkstyle一键设置了我的控件style, 如下
class MainWindow(QMainWindow):
    theme_changed = pyqtSignal(bool)
    
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.setWindowTitle("iCell")
        self.setGeometry(100, 100, 800, 600)
        self._init_theme()

    def _init_theme(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette))

需求：
帮我设计一个库，重新设计qt所有常见的window、widgets控件的格式、文字、间隔等待Style，

要求：
1. 使用方式类似于qdarkstyle，要求接口简单
2. 设计一套风格即可，也是Light风格，目前这个qdarkstyle的LightPalette都是黑灰白设计不太好，我喜欢黑白加浅蓝色（#057DCE）或者亮蓝色（#37AEFE）作为主基调


其它信息：
1. https://github.com/ColinDuquesnoy/QDarkStyleSheet
2. LightPalette的代码
"""QDarkStyle default light palette."""

# Local imports
from qdarkstyle.colorsystem import Blue, Gray
from qdarkstyle.palette import Palette


class LightPalette(Palette):
    """Theme variables."""

    ID = 'light'

    # Color
    COLOR_BACKGROUND_1 = Gray.B140
    COLOR_BACKGROUND_2 = Gray.B130
    COLOR_BACKGROUND_3 = Gray.B120
    COLOR_BACKGROUND_4 = Gray.B110
    COLOR_BACKGROUND_5 = Gray.B100
    COLOR_BACKGROUND_6 = Gray.B90

    COLOR_TEXT_1 = Gray.B10
    COLOR_TEXT_2 = Gray.B20
    COLOR_TEXT_3 = Gray.B50
    COLOR_TEXT_4 = Gray.B70

    COLOR_ACCENT_1 = Blue.B130
    COLOR_ACCENT_2 = Blue.B100
    COLOR_ACCENT_3 = Blue.B90
    COLOR_ACCENT_4 = Blue.B80
    COLOR_ACCENT_5 = Blue.B70
    
    # Color for disabled elements
    COLOR_DISABLED = Gray.B80

    OPACITY_TOOLTIP = 230


class Gray:
    B0 = '#000000'
    B10 = '#19232D'
    B20 = '#293544'
    B30 = '#37414F'
    B40 = '#455364'
    B50 = '#54687A'
    B60 = '#60798B'
    B70 = '#788D9C'
    B80 = '#9DA9B5'
    B90 = '#ACB1B6'
    B100 = '#B4B8BC'
    B110 = '#C0C4C8'
    B120 = '#D2D5D8'
    B130 = '#DFE1E2'
    B140 = '#FAFAFA'
    B150 = '#FFFFFF'


class Blue:
    B0 = '#000000'
    B10 = '#062647'
    B20 = '#26486B'
    B30 = '#375A7F'
    B40 = '#346792'
    B50 = '#1A72BB'
    B60 = '#057DCE'
    B70 = '#259AE9'
    B80 = '#37AEFE'
    B90 = '#73C7FF'
    B100 = '#9FCBFF'
    B110 = '#C2DFFA'
    B120 = '#CEE8FF'
    B130 = '#DAEDFF'
    B140 = '#F5FAFF'
    B150 = '#FFFFFF'

