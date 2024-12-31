from abc import ABC, abstractmethod


class FileHandler(ABC):
    """Abstract class: File handling interface"""
    @abstractmethod
    def open_file(self, file_path: str):
        pass

    @abstractmethod
    def save_file(self, file_path: str, content: str):
        pass

class FileHandlerImpl(FileHandler):
    """File handling implementation"""
    def open_file(self, file_path: str):
        print(f"Opening file: {file_path}")
        # Implement file opening logic here

    def save_file(self, file_path: str, content: str):
        print(f"Saving file: {file_path}")
        # Implement file saving logic here
