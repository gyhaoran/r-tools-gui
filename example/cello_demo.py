import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QTextEdit, QTabWidget, QTreeWidget, QTreeWidgetItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cello")
        self.setGeometry(100, 100, 1000, 800)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Initialize library data
        self.library_data = {
            "FinFET DH": ["SDBDHAND2LP", "SDBDHAND2_X0P5", "SDBDHAND2_X1", "SDBDHAND2_X2", "SDBDHAO21_LP", "SDBDHAO21_X0P5", "SDBDHAO21_X1", "SDBDHAO21_X2", "SDBDHAO221_LP", "SDBDHAO221_X0P5", "SDBDHAO221_X1", "SDBDHAO21_X2", "SDBDHAO121_LP", "SDBDHAO121_X0P5", "SDBDHAO121_X1", "SDBDHAO121_X2", "SDBDHAO121_LP", "SDBDHAO1221_X0P5", "SDBDHAO1221_X1", "SDBDHAO1221_X2", "SDBDHBUFLP", "SDBDHBUFX0P5", "SDBDHBUFX1", "SDBDHBUFX2", "SDBDHBUFX4", "SDBDHBUFX8", "SDBDHDFFX0P5", "SDBDHDFFX1", "SDBDHDFFX2", "SDBDHINVLP", "SDBDHINV_X0P5", "SDBDHINV_X1", "SDBDHINV_X2", "SDBDHINV_X4", "SDBDHINV_X8", "SDBDHLHX0P5", "SDBDHLHX1", "SDBDHLH_X2", "SDBDHLLX0P5", "SDBDHLLX1", "SDBDHLLX2", "SDBDHNAND2LP"],
            "FinFET_SR": ["Cell_A", "Cell_B", "Cell_C", "Cell_D", "Cell_E"]  # Example data for the second library
        }

        # Library Browser Tab (Original)
        self.library_browser_tab = QWidget()
        self.tab_widget.addTab(self.library_browser_tab, "Library Browser")

        # Library Browser layout (Original)
        self.setup_library_browser_tab()

        # Library Browser2 Tab (Modified)
        self.library_browser2_tab = QWidget()
        self.tab_widget.addTab(self.library_browser2_tab, "Library Browser2")

        # Library Browser2 layout (Modified)
        self.setup_library_browser2_tab()

        # Other Tabs
        self.library_status_tab = QWidget()
        self.view_browser_tab = QWidget()
        self.job_manager_tab = QWidget()

        self.tab_widget.addTab(self.library_status_tab, "Library Status")
        self.tab_widget.addTab(self.view_browser_tab, "View Browser")
        self.tab_widget.addTab(self.job_manager_tab, "Job Manager")

    def setup_library_browser_tab(self):
        # Original Library Browser layout
        library_browser_layout = QHBoxLayout()
        self.library_browser_tab.setLayout(library_browser_layout)

        # Column 1: Libraries
        libraries_layout = QVBoxLayout()

        self.libraries_label = QLabel("Libraries")
        self.libraries_list = QListWidget()
        self.libraries_list.addItems(["FinFET DH", "FinFET_SR"])
        self.libraries_list.itemDoubleClicked.connect(self.show_cells)

        libraries_layout.addWidget(self.libraries_label)
        libraries_layout.addWidget(self.libraries_list)

        library_browser_layout.addLayout(libraries_layout)

        # Column 2: Cells
        cells_layout = QVBoxLayout()

        self.cells_label = QLabel("Cells")
        self.cells_list = QListWidget()
        self.cells_list.itemDoubleClicked.connect(self.show_details)

        cells_layout.addWidget(self.cells_label)
        cells_layout.addWidget(self.cells_list)

        library_browser_layout.addLayout(cells_layout)

        # Column 3: Layouts, Topologies, Circuits
        details_layout = QVBoxLayout()

        # Layouts
        self.layouts_label = QLabel("Layouts")
        self.layouts_display = QTextEdit()
        self.layouts_display.setReadOnly(True)

        details_layout.addWidget(self.layouts_label)
        details_layout.addWidget(self.layouts_display)

        # Topologies
        self.topologies_label = QLabel("Topologies")
        self.topologies_display = QTextEdit()
        self.topologies_display.setReadOnly(True)

        details_layout.addWidget(self.topologies_label)
        details_layout.addWidget(self.topologies_display)

        # Circuits
        self.circuits_label = QLabel("Circuits")
        self.circuits_display = QTextEdit()
        self.circuits_display.setReadOnly(True)

        details_layout.addWidget(self.circuits_label)
        details_layout.addWidget(self.circuits_display)

        library_browser_layout.addLayout(details_layout)

    def setup_library_browser2_tab(self):
        # Modified Library Browser2 layout
        library_browser2_layout = QHBoxLayout()
        self.library_browser2_tab.setLayout(library_browser2_layout)

        # Column 1: Tree (Libraries and Cells)
        tree_layout = QVBoxLayout()

        self.tree_label = QLabel("Libraries and Cells")
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Library/Cell")
        self.tree_widget.itemDoubleClicked.connect(self.show_details2)

        # Populate the tree with library data
        for library, cells in self.library_data.items():
            library_item = QTreeWidgetItem(self.tree_widget)
            library_item.setText(0, library)
            for cell in cells:
                cell_item = QTreeWidgetItem(library_item)
                cell_item.setText(0, cell)

        tree_layout.addWidget(self.tree_label)
        tree_layout.addWidget(self.tree_widget)

        library_browser2_layout.addLayout(tree_layout)

        # Column 2: Layouts
        layouts_layout = QVBoxLayout()

        self.layouts_label2 = QLabel("Layouts")
        self.layouts_display2 = QTextEdit()
        self.layouts_display2.setReadOnly(True)

        layouts_layout.addWidget(self.layouts_label2)
        layouts_layout.addWidget(self.layouts_display2)

        library_browser2_layout.addLayout(layouts_layout)

        # Column 3: Topologies and Circuits
        details_layout2 = QVBoxLayout()

        # Topologies
        self.topologies_label2 = QLabel("Topologies")
        self.topologies_display2 = QTextEdit()
        self.topologies_display2.setReadOnly(True)

        details_layout2.addWidget(self.topologies_label2)
        details_layout2.addWidget(self.topologies_display2)

        # Circuits
        self.circuits_label2 = QLabel("Circuits")
        self.circuits_display2 = QTextEdit()
        self.circuits_display2.setReadOnly(True)

        details_layout2.addWidget(self.circuits_label2)
        details_layout2.addWidget(self.circuits_display2)

        library_browser2_layout.addLayout(details_layout2)

    def show_cells(self, item):
        # Load cells for the selected library
        library_name = item.text()
        self.cells_list.clear()
        self.cells_list.addItems(self.library_data.get(library_name, []))

    def show_details(self, item):
        # Show details for the selected cell
        cell_name = item.text()
        self.layouts_display.setText(f"Layout for {cell_name}")
        self.topologies_display.setText("Topologies data not available")  # Placeholder
        self.circuits_display.setText(f"Schematic for {cell_name}")

    def show_details2(self, item):
        # Show details for the selected cell in Library Browser2
        if item.parent() is not None:  # Check if it's a cell (not a library)
            cell_name = item.text(0)
            self.layouts_display2.setText(f"Layout for {cell_name}")
            self.topologies_display2.setText("Topologies data not available")  # Placeholder
            self.circuits_display2.setText(f"Schematic for {cell_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())