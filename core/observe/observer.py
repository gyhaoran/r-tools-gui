from abc import ABC, abstractmethod


class Observer(ABC):
    """Abstract class: Observer interface"""
    @abstractmethod
    def update(self):
        pass
