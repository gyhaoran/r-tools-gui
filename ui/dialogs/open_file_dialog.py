import os
from PyQt5.QtWidgets import QFileDialog
from core import library_manager, LibraryManager


class OpenFileDialog:
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow

    def open_file(self):
        """Open file dialog to select files and load them into the library manager."""
        file = self._get_file_path()
        if not file:
            return

        file_extension = self._get_file_extension(file)
        if not file_extension:
            return

        self._load_file(file, file_extension)

    def _get_file_path(self):
        """Open a file dialog and return the selected file path."""
        file, _ = QFileDialog.getOpenFileName(self.mainwindow, "Open File", "", 
                                              "LEF Files (*.lef);;DEF Files (*.def);;Spice Files (*.sp);;GDS Files (*.gds;*.gdsII);;All Files (*)")
        return file

    def _get_file_extension(self, file):
        """Extract and validate the file extension."""
        file_extension = os.path.splitext(file)[1].lower()[1:]
        if file_extension not in ['lef', 'def', 'sp', 'gds', 'gdsii']:
            print("Unsupported file type.")
            return None
        return file_extension

    def _load_file(self, file, file_extension):
        """Load the file into the library manager based on its extension."""
        loader_map = {
            'lef': library_manager().load_lef_file,
            'def': library_manager().load_def_file,
            'sp': library_manager().load_spice_file,
            'gds': library_manager().load_gds_file,
            'gdsii': library_manager().load_gds_file,
        }
        loader = loader_map.get(file_extension)
        if loader:
            loader(file)
            