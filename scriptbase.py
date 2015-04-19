#/usr/bin/python3
"""Simple "loader" for use in multiple scripts pointing to the same endpoint"""

from domoticz_control import Domoticz
import os

BASE_URI   = "http://127.0.0.1:8080/"
AUTH_FILE  = "creds.asc"

def get_domoticz():
    AuthString = open(AUTH_FILE, "r").read()
    return Domoticz(BASE_URI).authorize_header(AuthString)