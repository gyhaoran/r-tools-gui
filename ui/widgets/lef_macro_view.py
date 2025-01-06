from backend.lef_parser import LefDscp, draw_macro
from core.observe import Observer
from core import library_manager, LibraryManager

from matplotlib.figure import Figure
from matplotlib.colors import to_rgba
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class LefMacroView(QWidget):
    def __init__(self, lef_dscp: LefDscp=None, parent=None):
        super().__init__(parent)

        self.lef_dscp = lef_dscp

        # Create a figure and canvas to draw on
        self.figure = Figure(figsize=(12, 9))
        self.canvas = FigureCanvas(self.figure)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.text_color = '#000000'  # Default text color (black for light mode)
        self.set_theme(False)  # Assuming light mode is the default

    def set_theme(self, dark_mode=False):
        """Set the theme for the figure and canvas."""
        if dark_mode:
            bg_color = '#19232D'
            self.text_color = '#ffffff'  # White text for dark mode
        else:
            bg_color = '#FAFAFA'
            self.text_color = '#000000'  # Black text for light mode
        
        self.figure.patch.set_facecolor(bg_color)
        self.canvas.setStyleSheet(f"background-color: {bg_color};")
        
        # Update text colors for all axes in the current figure
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
            # If there are any other text elements, they should be updated here as well
            for spine in ax.spines.values():
                spine.set_edgecolor(to_rgba(text_color, alpha=0.5))  # Optionally change spine color

    def draw_cells(self, to_draw):
        """Draw cells based on LEF information."""
        self.figure.clear()  # Clear the previous plots
        
        num_plots = len(to_draw)
        for idx, macro_name in enumerate(to_draw, start=1):
            if macro_name not in self.lef_dscp.macros:
                print(f"Error: Macro '{macro_name}' does not exist in the parsed library.")
                continue
            
            macro = self.lef_dscp.macros[macro_name]
            
            sub = self.figure.add_subplot(1, num_plots, idx)
            sub.set_title(macro.name, color=self.text_color)  # Use the defined text color
            draw_macro(macro, ax=sub)
            
            sub.autoscale_view()

        # Refresh canvas
        self.update_text_colors(self.text_color)
        self.canvas.draw()

    def update_lef(self, lef_dscp: 'LefDscp'):
        self.lef_dscp = lef_dscp

    # Observer method, python use duck type
    def update(self):
        self.update_lef(library_manager().lef_dscp)
        