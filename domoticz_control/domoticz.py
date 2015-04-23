#!/usr/bin/python3

from .device import *
from .agent import *

class Domoticz:
    """Represents a Domoticz endpoint"""

    def __init__(self, baseUri):
        self._agent = Agent(baseUri)

    def authorize_header(self, header):
        """Sets the base64 encoded Basic Authorization HTTP header value"""
        self._agent.authorize_header(header)
        return self

    def authorize(self, username, password):
        """Sets the Authorization HTTP header based on the given username and password"""
        self._agent.authorize(username, password)
        return self

    def preload(self):
        self.get_all_device_states()
        return self

    def get_all_device_states(self):
        """Gets a list of all devices and device-related information. Device array in get_all_device_states()['result']"""
        return self._agent.get_all_device_states()

    def get_device_state(self, identifier):
        """Gets the state of the device with the given id (if identifier is an integer) or name"""
        return self._agent.get_device_state(identifier)

    def get_device(self, identifier):
        state = self.get_device_state(identifier);
        return Device(self, state) if state else None;

    @property
    def temperature_unit(self):
        unit = self.get_all_device_states()["TempSign"]
        return "°" + unit

    def format_temperature(self, t, tempFormat=".1f"):
        return ("{:" + tempFormat + "}{}").format(t, self.temperature_unit)

    def invalidate(self):
        self._agent.invalidate()

    def invalidate_device(self, identifier):
        self._agent.invalidate_device(identifier)