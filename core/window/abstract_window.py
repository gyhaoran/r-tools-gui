from abc import ABC, abstractmethod
from .window_manager import window_manager, WindowManager


class AbstractWindow(ABC):
    """Abstract class: Observer interface"""
    
    def __init__(self, win_id: str):
        window_manager().add_window(win_id, self)
    
    @abstractmethod
    def widget(self):
        pass
    
    @abstractmethod
    def area(self):
        """ LeftDockWidgetArea, RightDockWidgetArea, TopDockWidgetArea, BottomDockWidgetArea, DockWidgetArea_Mask, AllDockWidgetAreas, NoDockWidgetArea """
        pass
    
    @abstractmethod
    def is_center(self):
        pass
