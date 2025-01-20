from backend.lef_parser import LefDscp, draw_macro
from core import library_manager
from matplotlib.figure import Figure
from matplotlib.colors import to_rgba
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class LefMacroView(QWidget):
    def __init__(self, lef_dscp: LefDscp = None, parent=None):
        super().__init__(parent)
        self.lef_dscp = lef_dscp
        self.text_color = '#000000'  # Default text color (black for light mode)
        self.init_ui()
        self.set_theme(False)  # Assuming light mode is the default
        self.setMinimumWidth(350)

    def init_ui(self):
        """Initialize the UI components."""
        self.figure = Figure(figsize=(12, 9))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def set_theme(self, dark_mode=False):
        """Set the theme for the figure and canvas."""
        bg_color = '#19232D' if dark_mode else '#FAFAFA'
        self.text_color = '#ffffff' if dark_mode else '#000000'

        self.figure.patch.set_facecolor(bg_color)
        self.canvas.setStyleSheet(f"background-color: {bg_color};")
        self.update_text_colors(self.text_color)
        self.canvas.draw_idle()

    def update_text_colors(self, text_color):
        """Update text colors of all elements within the figure."""
        for ax in self.figure.axes:
            ax.title.set_color(text_color)
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.tick_params(axis='x', colors=text_color)
            ax.tick_params(axis='y', colors=text_color)
            for spine in ax.spines.values():
                spine.set_edgecolor(to_rgba(text_color, alpha=0.5))

    def draw_cells(self, to_draw):
        """Draw cells based on LEF information."""
        self.figure.clear()  # Clear the previous plots

        num_plots = len(to_draw)
        for idx, macro_name in enumerate(to_draw, start=1):
            if macro_name not in self.lef_dscp.macros:
                print(f"Error: Macro '{macro_name}' does not exist in the parsed library.")
                continue

            macro = self.lef_dscp.macros[macro_name]
            self.draw_macro_subplot(macro, idx, num_plots)

        self.update_text_colors(self.text_color)
        self.canvas.draw()

    def draw_macro_subplot(self, macro, idx, num_plots):
        """Draw a single macro in a subplot."""
        sub = self.figure.add_subplot(1, num_plots, idx)
        sub.set_title(macro.name, color=self.text_color)
        draw_macro(macro, ax=sub)
        sub.autoscale_view()

    def update_lef(self, lef_dscp: LefDscp):
        """Update the LEF description."""
        self.lef_dscp = lef_dscp

    def update(self):
        """Clear the figure and update the LEF description."""
        self.figure.clear()
        self.canvas.draw()
        self.update_lef(library_manager().lef_dscp)
