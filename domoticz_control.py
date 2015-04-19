#!/usr/bin/python3
"""domoticz_control.py: wraps the Domoticz JSON API and exposes a simpler interface for use in Python3 scripts."""

import urllib.parse
import urllib.request
import json
import base64

class Domoticz:
    """Represents a Domoticz endpoint"""

    def __init__(self, baseUri):
        self._baseUri = baseUri
        self._auth = None
        self._cachedDevices = None

    def _validate_permission(self):
        if self._auth == None:
            raise PermissionError("Unauthorized. Call authorize_header(header)/authorize(user, pass)")

    def invalidate_cache(self):
        self._cachedDevices = None

    def authorize_header(self, header):
        """Sets the base64 encoded Basic Authorization HTTP header value"""
        self._auth = header
        return self

    def authorize(self, username, password):
        """Sets the Authorization HTTP header based on the given username and password"""
        return self.authorize_header( base64.b64encode("{}:{}".format(username, password)) )

    def preload(self):
        self.get_all_device_states()
        return self

    def request(self, qd):
        """Sends a direct request to Domoticz with the GET data in the dictionary qd"""
        self._validate_permission()
        url = self._baseUri + "json.htm?" + urllib.parse.urlencode(qd)
        req = urllib.request.Request(url, headers={"Authorization": "Basic " + self._auth})

        return json.loads( urllib.request.urlopen(req).read().decode('utf-8') )

    def get_all_device_states(self):
        """Gets a list of all devices and device-related information. Device array in get_all_device_states()['result']"""
        if not self._cachedDevices:
            self._cachedDevices = self.request({
                "type": "devices", 
                "filter": "all"
            })

        return self._cachedDevices

    def get_device_state(self, identifier):
        """Gets the state of the device with the given id (if identifier is an integer) or name"""
        idAttrib = 'idx' if isinstance(identifier, int) else 'Name'

        identifier = str(identifier) # idx as returned by domoticz is... for some reason... a string

        devices = self.get_all_device_states().get("result")
        for d in devices:
            if d[idAttrib] == identifier:
                return d

        return None

    def get_device(self, identifier):
        state = self.get_device_state(identifier);
        return Device(self, state) if state else None;

    def get_temperature_unit(self):
        unit = self.get_all_device_states()["TempSign"]
        return ("°" + unit) if unit != "K" else unit

    def format_temperature(self, t, tempFormat=".1f"):
        return ("{:" + tempFormat + "}{}").format(t, self.get_temperature_unit())

class Device:
    """Wraps a Domoticz device and provides methods to read values and change state."""

    def __init__(self, domoticz, state):
        self.id = int(state['idx'])
        self.name = state['Name']
        self.capabilities = []

        self._domoticz = domoticz
        self._detect_capabilities()

    #Internals
    def _assert_capability(self, c):
        if not (c in self.capabilities):
            raise TypeError("Can't do that! I have the following capabilities: " + ', '.join(self.capabilities))

    def _get_state(self, value=None):
        state = self._domoticz.get_device_state(self.id)
        return state.get(value) if (state and value) else state

    def _detect_capabilities(self):
        switchType = self._get_state("SwitchType")
        if switchType:
            self.capabilities += ["switch"]
            if switchType == "Dimmer":
                self.capabilities += ["dim"]

        if self._get_state("Temp"):
            self.capabilities += ["thermometer"]

        if self._get_state("Humidity"):
            self.capabilities += ["hygrometer"]

    def _request(self, qd):
        return self._domoticz.request(qd)

    #Output
    def __str__(self):
        return str(self.id) if not self.name else "{0.name} ({0.id})".format(self)

    def readout(self):
        out = [str(self)]
        if "switch" in self.capabilities:
            out += ["Switch status: " + ("ON" if self.is_on() else "OFF")]
        if "dim" in self.capabilities:
            out += ["Dimmer level: {0:.0%}".format( self.get_level() )]
        if "thermometer" in self.capabilities:
            out += ["Temperature: {0}".format( self.get_temperature() )]
        if "hygrometer" in self.capabilities:
            out += ["Humidity: {0:.0%}".format( self.get_humidity() )]

        return '\n'.join(out);

    #Switch functionality
    def is_on(self):
        self._assert_capability("switch")
        return self._get_state("Status") != "Off"

    def switch(self, state):
        self._assert_capability("switch")
        self._request({
            "type": "command",
            "param": "switchlight",
            "idx": self.id,
            "switchcmd": "On" if state else "Off",
        })

    def get_level(self):
        return (self._get_state("Level") / 100.0) if self.is_on() else 0;

    def set_level(self, level):
        self._assert_capability("dim")
        self._request({
            "type": "command",
            "param": "switchlight",
            "idx": self.id,
            "switchcmd": "Set Level",
            "level": round(level * 16)
        })

    #Climate functionality
    def get_temperature(self):
        self._assert_capability("thermometer")
        return self._get_state("Temp")

    def get_humidity(self):
        self._assert_capability("hygrometer")
        return self._get_state("Humidity") / 100.0
