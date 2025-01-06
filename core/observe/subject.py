from .observer import Observer


class Subject():
    """This class represents an observable object, or "data" in the model-view paradigm."""
    
    def __init__(self) -> None:
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
        
    def remove_observer(self, observer):
        self.observers.remove(observer)
        
    def notify(self):
        for observer in self.observers:
            observer.update()
