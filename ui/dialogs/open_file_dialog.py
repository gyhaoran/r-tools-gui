import os
from PyQt5.QtWidgets import QFileDialog
from core import library_manager, LibraryManager

class OpenFileDialog():
    
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow

    def open_file(self):
        """Open file dialog to select files."""
        file, _ = QFileDialog.getOpenFileName(self.mainwindow, "Open File", "", "LEF Files (*.lef);;DEF Files (*.def);;Spice Files (*.sp);;GDS Files (*.gds;*.gdsII);;All Files (*)")
        if file:           
            file_extension = os.path.splitext(file)[1].lower()[1:]            
            if file_extension in ['lef']:
                library_manager().load_lef_file(file)
            elif file_extension in ['def']:
                library_manager().load_def_file(file)
            elif file_extension in ['sp']:
                library_manager().load_spice_file(file)
            elif file_extension in ['gds', 'gdsii']:
                library_manager().load_gds_file(file)
            else:
                print("Unsupported file type.")
                return