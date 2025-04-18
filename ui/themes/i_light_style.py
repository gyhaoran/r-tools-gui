from qtpy.QtCore import Qt
from qtpy.QtGui import QColor, QPalette

class iLightPalette:
    """Color system for light theme with blue accent (updated to match provided QSS)"""
    # Base colors
    PRIMARY_BLUE = '#057DCE'
    SECONDARY_BLUE = '#37AEFE'
    BACKGROUND = '#FAFAFA'
    FOREGROUND = '#19232D'
    BORDER = '#dfe3e7'
    DISABLED = '#9DA9B5'
    HIGHLIGHT = '#E6F3FD'
    SELECTION = '#9FCBFF'
    ERROR_RED = '#D32F2F'
    WARNING_ORANGE = '#F57C00'
    SUCCESS_GREEN = '#388E3C'
    TOOLBAR_BG = '#dfe3e7'
    MEDIUM_GRAY = '#ACB1B6'
    HIGHLIGHT_BLUE = '#73C7FF'

    @classmethod
    def get_palette(cls):
        """Create QPalette configuration"""
        palette = QPalette()
        # Base colors
        palette.setColor(QPalette.Window, QColor(cls.BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(cls.FOREGROUND))
        palette.setColor(QPalette.Base, QColor(cls.BACKGROUND))
        palette.setColor(QPalette.AlternateBase, QColor(cls.HIGHLIGHT))
        palette.setColor(QPalette.ToolTipBase, QColor(cls.BACKGROUND))
        palette.setColor(QPalette.ToolTipText, QColor(cls.FOREGROUND))
        palette.setColor(QPalette.Text, QColor(cls.FOREGROUND))
        palette.setColor(QPalette.Button, QColor(cls.BACKGROUND))
        palette.setColor(QPalette.ButtonText, QColor(cls.FOREGROUND))
        palette.setColor(QPalette.BrightText, QColor(cls.ERROR_RED))
        palette.setColor(QPalette.Link, QColor(cls.PRIMARY_BLUE))
        palette.setColor(QPalette.Highlight, QColor(cls.SELECTION))
        palette.setColor(QPalette.HighlightedText, QColor(cls.FOREGROUND))
        
        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(cls.DISABLED))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(cls.DISABLED))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(cls.DISABLED))
        return palette

    @classmethod
    def get_stylesheet(cls):
        """Generate complete QSS stylesheet with integrated rules"""
        return f"""
        /* ================ Global Reset ================ */
        * {{
            padding: 0px;
            margin: 0px;
            border: 0px;
            border-style: none;
            border-image: none;
            outline: 0;
        }}

        QToolBar * {{
            margin: 0px;
            padding: 0px;
        }}

        /* ================ Base Widget Styles ================ */
        QWidget {{
            background-color: {cls.BACKGROUND};
            color: {cls.FOREGROUND};
            selection-background-color: {cls.SELECTION};
            selection-color: {cls.FOREGROUND};
            font-family: 'Segoe UI';
            font-size: 9pt;
            border-radius: 4px;
        }}

        QWidget:disabled {{
            background-color: {cls.BACKGROUND};
            color: {cls.DISABLED};
        }}

        /* ================ Main Window ================ */
        QMainWindow::separator {{
            background-color: {cls.BORDER};
            border: 0px solid {cls.BACKGROUND};
            padding: 2px;
        }}

        QMainWindow::separator:hover {{
            background-color: {cls.MEDIUM_GRAY};
            border: 0px solid {cls.SECONDARY_BLUE};
        }}

        QMainWindow::separator:horizontal {{
            width: 5px;
            image: url(":/qss_icons/light/rc/toolbar_separator_vertical.png");
        }}

        QMainWindow::separator:vertical {{
            height: 5px;
            image: url(":/qss_icons/light/rc/toolbar_separator_horizontal.png");
        }}

        /* ================ Containers ================ */
        QDockWidget {{
            border: 1px solid {cls.BORDER};
            titlebar-close-icon: url(:/qss_icons/rc/close_dark.png);
            titlebar-normal-icon: url(:/qss_icons/rc/undock_dark.png);
        }}

        QDockWidget::title {{
            background: {cls.TOOLBAR_BG};
            padding: 4px;
            border-bottom: 2px solid {cls.PRIMARY_BLUE};
        }}

        QGroupBox {{
            border: 1px solid {cls.BORDER};
            margin-top: 1.5em;
            padding-top: 0.5em;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            color: {cls.PRIMARY_BLUE};
        }}

        /* ================ Data Views ================ */
        QTableView, QTreeView, QListView {{
            alternate-background-color: {cls.HIGHLIGHT};
            border: 1px solid {cls.BORDER};
            gridline-color: {cls.BORDER};
        }}

        QHeaderView::section {{
            background: {cls.BACKGROUND};
            color: {cls.FOREGROUND};
            border: 1px solid {cls.BORDER};
            padding: 4px;
        }}

        /* ================ Input Controls ================ */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            border: 1px solid {cls.BORDER};
            border-radius: 4px;
            padding: 3px;
        }}

        QComboBox {{
            border: 1px solid {cls.BORDER};
            border-radius: 4px;
            padding: 3px 18px 3px 5px;
        }}

        QComboBox::drop-down {{
            border-left: 1px solid {cls.BORDER};
        }}

        /* ================ Buttons ================ */
        QPushButton {{
            background-color: {cls.TOOLBAR_BG};
            color: {cls.FOREGROUND};
            border-radius: 4px;
            padding: 5px 10px;
            min-width: 60px;
        }}

        QPushButton:hover {{
            background-color: {cls.MEDIUM_GRAY};
        }}

        QPushButton:pressed {{
            background-color: {cls.SECONDARY_BLUE};
            color: white;
        }}

        /* ================ Scrollbars ================ */
        QScrollBar:vertical {{
            width: 12px;
            background: {cls.BACKGROUND};
        }}

        QScrollBar::handle:vertical {{
            background: {cls.BORDER};
            min-height: 20px;
        }}

        /* ================ Tabs ================ */
        QTabBar::tab {{
            background: {cls.BACKGROUND};
            border: 1px solid {cls.BORDER};
            padding: 8px 12px;
        }}

        QTabBar::tab:selected {{
            border-bottom: 2px solid {cls.PRIMARY_BLUE};
            background: {cls.HIGHLIGHT};
        }}

        /* ================ Menus & Toolbars ================ */
        QMenu {{
            border: 1px solid {cls.BORDER};
            background: {cls.TOOLBAR_BG};
        }}

        QMenu::item:selected {{
            background: {cls.SELECTION};
        }}

        QToolBar {{
            background: {cls.TOOLBAR_BG};
            border-bottom: 1px solid {cls.BORDER};
        }}

        /* ================ Status Bar ================ */
        QStatusBar {{
            border: 1px solid {cls.BORDER};
            background: {cls.TOOLBAR_BG};
        }}

        /* ================ Checkboxes & Radios ================ */
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 14px;
            height: 14px;
        }}

        QCheckBox::indicator:checked {{
            image: url(":/qss_icons/light/rc/checkbox_checked.png");
        }}

        /* ================ Spin Boxes ================ */
        QAbstractSpinBox {{
            border: 1px solid {cls.BORDER};
            border-radius: 4px;
            padding: 2px;
        }}

        /* ================ Sliders ================ */
        QSlider::groove:horizontal {{
            height: 4px;
            background: {cls.BORDER};
        }}

        QSlider::handle:horizontal {{
            background: {cls.PRIMARY_BLUE};
            width: 12px;
        }}

        /* ================ Dialogs ================ */
        QDialog {{
            background: {cls.BACKGROUND};
            border: 1px solid {cls.BORDER};
        }}

        /* ================ Tree View ================ */
        QTreeView::branch:open {{
            image: url(":/qss_icons/light/rc/branch_open.png");
        }}

        /* Add more styles from the provided QSS here... */
        """

def load_stylesheet(palette=iLightPalette):
    """One-line style loader"""
    with open('ui/themes/light.qss', 'r') as fin:
        style_sheet= fin.read()
    return style_sheet