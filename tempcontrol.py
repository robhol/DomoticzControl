#!/usr/bin/python3
"""tempcontrol.py: an implementation of a simple thermostat using domoticz_control"""

import scriptbase

domoticz = scriptbase.get_domoticz().preload()

def RangeFromSetpoint(sp, tolerance):
    return [sp - tolerance, sp + tolerance]

DEBUG_NONE   = 99
DEBUG_ERROR  = 3
DEBUG_ACTION = 2
DEBUG_STATE  = 1

def debug(s, msglevel, threshold):
    print(s) if msglevel >= threshold else None

def tsdebug(thermostat, msg, level):
    thlevel = thermostat.get("debug") or DEBUG_NONE
    debug("{:>16}: {}".format(
        "{} ({})".format(thermostat["name"], thermostat["thermometer_id"]), 
        msg), level, thlevel)

def boundary_debug_message(thermostat, thermometer, switch, ideal, extreme, is_low):
    temp = thermometer.temperature
    switching = switch.is_on != is_low

    tsdebug(thermostat,
        "<!> {temp} is {delta} {preposition} {extreme_type}, {delta_ideal} {preposition} ideal. {switch} {switch_action} switched {switch_state}.".format(
                temp =            domoticz.format_temperature(temp),
                delta =           domoticz.format_temperature( abs(extreme - temp), ".2f" ),
                delta_ideal =     domoticz.format_temperature( abs(ideal - temp), ".2f" ),
                preposition =     "below"     if is_low else    "above",
                extreme_type =    "minimum"   if is_low else    "maximum",
                switch =          switch,
                switch_action =   "will be"   if switching else "is already",
                switch_state =    "on"        if is_low else    "off",
            ),
        DEBUG_ACTION)

thermostats = [
    {
        "name": "Living room", 
        "range": RangeFromSetpoint(22.0, 0.25),

        "switch_id": 8, 
        "thermometer_id": 9, 
        
        "debug": DEBUG_STATE
    },
    {
        "name": "Bedroom", 
        "range": RangeFromSetpoint(20.5, 0.75),

        "switch_id": 12, 
        "thermometer_id": 11, 

        "debug": DEBUG_STATE
    },
]

statuses = []

for thermostat in thermostats:
    thermometer = domoticz.get_device(thermostat["thermometer_id"])
    switch      = domoticz.get_device(thermostat["switch_id"])

    temp = thermometer.temperature

    min_temp = thermostat["range"][0]
    max_temp = thermostat["range"][1]
    ideal_temp = (min_temp + max_temp) / 2

    state_change = None

    if temp < min_temp:
        state_change = True
    elif temp > max_temp:
        state_change = False
    else:
        tsdebug(thermostat,
            "(i) Temperature is within range: {} -> {} <- {}. Ideal temperature is {} ({})".format(
                domoticz.format_temperature(min_temp),
                domoticz.format_temperature(temp),
                domoticz.format_temperature(max_temp),
                domoticz.format_temperature(ideal_temp),
                domoticz.format_temperature(temp - ideal_temp, "+.2f")),
            DEBUG_STATE)
        continue

    boundary_debug_message(thermostat, thermometer, switch, ideal_temp, extreme=min_temp if state_change else max_temp, is_low=state_change)
    switch.switch(state_change)
