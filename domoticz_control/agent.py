#!/usr/bin/python3

import urllib.parse
import urllib.request
import json
import base64

class Agent:
    """Handles requests and caching"""
    def __init__(self, baseUri):
        self._baseUri = baseUri
        self.data = None
        self._auth = None

        self._invalidatedDevices = []

    def _patch_device_result(self, index, newdata):
        """ A request for a single device's state also includes "general" domoticz data; we want to update that as well as the specific device's state """
        for k, v in newdata.items():
            if k != "result":
                self.data[k] = v

        self.data["result"][index] = newdata["result"][0]

    def _request_single_device_state(self, idx):
        full_state = self.request({
                "type": "devices", 
                "rid": str(idx)
            })
        return full_state["result"][0], full_state

    def _find_device_state(self, identifier):
        devices = self.get_all_device_states()["result"]
        idAttrib = 'idx' if isinstance(identifier, int) else 'Name'
        identifier = str(identifier) # idx as returned by domoticz is... for some reason... a string
        for i, d in enumerate(devices):
            if d[idAttrib] == identifier:
                return d, i
        return None, None

    def _validate_permission(self):
        if self._auth == None:
            raise PermissionError("Unauthorized. Call authorize_header(header)/authorize(user, pass)")

    def request(self, queryDict):
        self._validate_permission()
        querystring = urllib.parse.urlencode(queryDict)

        url = self._baseUri + "json.htm?" + querystring
        req = urllib.request.Request(url, headers={"Authorization": "Basic " + self._auth})

        return json.loads( urllib.request.urlopen(req).read().decode('utf-8') )

    def authorize_header(self, header):
        self._auth = header
        return self

    def authorize(self, username, password):
        return self.authorize_header( base64.b64encode("{}:{}".format(username, password).encode('utf-8')).decode('utf-8') )

    def get_all_device_states(self):
        if not self.data:
            self._invalidatedDevices = []
            self.data = self.request({
                "type": "devices"
            })

        return self.data

    def get_device_state(self, identifier):
        """Gets the state of the device with the given id (if identifier is an integer) or name"""

        state, list_index = self._find_device_state(identifier)
        idx = int(state['idx'])

        if idx in self._invalidatedDevices:
            state, full_state = self._request_single_device_state(idx)
            self._patch_device_result(list_index, full_state)
            self._invalidatedDevices.remove(idx)

        return state

    def invalidate_device(self, identifier):
        self._invalidatedDevices.append(int( self.get_device_state(identifier)['idx'] ))

    def invalidate(self):
        self.data = None