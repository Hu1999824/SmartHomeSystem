# device/sensorDevice.py
from .baseDevice import BaseDevice

class SensorDevice(BaseDevice):
    """Read-only devices, such as temperature, humidity, and air quality sensors."""
    def turn_on(self):
        return "The sensor cannot perform a switching operation."

    def turn_off(self):
        return "The sensor cannot perform a switching operation."

    def get_state(self):
        return self.controller.getDeviceStatus(self.entity_id)
