# device/switchDevice.py
from .baseDevice import BaseDevice

class SwitchDevice(BaseDevice):
    def turn_on(self):
        return self.controller.executeCommand(self.entity_id, "turn_on")

    def turn_off(self):
        return self.controller.executeCommand(self.entity_id, "turn_off")

    def get_state(self):
        return self.controller.getDeviceStatus(self.entity_id)
