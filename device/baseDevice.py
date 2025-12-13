# device/baseDevice.py
from abc import ABC, abstractmethod

class BaseDevice(ABC):
    def __init__(self, entity_id: str, controller):
        self.entity_id = entity_id
        self.controller = controller

    @abstractmethod
    def turn_on(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass

    @abstractmethod
    def get_state(self):
        pass
