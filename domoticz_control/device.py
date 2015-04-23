#!/usr/bin/python3

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
        return self._domoticz._agent.request(qd)

    #Output
    def __str__(self):
        return str(self.id) if not self.name else "{0.name} ({0.id})".format(self)

    def readout(self):
        out = [str(self)]
        if "switch" in self.capabilities:
            out += ["Switch status: " + ("ON" if self.is_on else "OFF")]
        if "dim" in self.capabilities:
            out += ["Dimmer level: {0:.0%}".format( self.dim_level )]
        if "thermometer" in self.capabilities:
            out += ["Temperature: {0}".format( self.temperature )]
        if "hygrometer" in self.capabilities:
            out += ["Humidity: {0:.0%}".format( self.humidity )]

        return '\n'.join(out);

    #Switch functionality
    @property
    def is_on(self):
        self._assert_capability("switch")
        return self._get_state("Status") != "Off"

    @property
    def dim_level(self):
        return (self._get_state("Level") / 100.0) if self.is_on else 0;

    def switch(self, state):
        self._assert_capability("switch")

        switchcmd = None
        if isinstance(state, str):
            switchcmd = state.capitalize()
            if switchcmd not in ["On", "Off"]:
                raise ValueError("switch(state) must be a boolean value or the string 'On' or 'Off'.")
        else:
            switchcmd = "On" if state else "Off"

        self._domoticz.invalidate_device(self.id)

        self._request({
            "type": "command",
            "param": "switchlight",
            "idx": self.id,
            "switchcmd": switchcmd,
        })

    def dim(self, level):
        self._assert_capability("dim")
        self._domoticz.invalidate_device(self.id)
        self._request({
            "type": "command",
            "param": "switchlight",
            "idx": self.id,
            "switchcmd": "Set Level",
            "level": round(level * 16)
        })

    #Climate functionality
    @property
    def temperature(self):
        self._assert_capability("thermometer")
        return self._get_state("Temp")

    @property
    def humidity(self):
        self._assert_capability("hygrometer")
        return self._get_state("Humidity") / 100.0
