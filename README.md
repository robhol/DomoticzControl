## DomoticzControl
A simple library for interacting with Domoticz using its JSON API.

###Example usage
Note that this is an early draft; syntax will probably change, and hopefully for the better. :)

```python
# Creating the object...
domoticz = Domoticz(BASE_URI).authorize("username", "hunter2")

# Accessing devices...
device = domoticz.get_device("heater") # ... by name
device = domoticz.get_device(11)       # ... by ID   (idx)

# Accessing device information
device.capabilities # List that may contain: "switch", "dim", "thermometer", "hygrometer"

# ... property      Possible values     Needs capability...
device.is_on        True, False         # switch, dim
device.dim_level    0.0 - 1.0           # dim 
device.temperature  (any float)         # thermometer
device.humidity     0.0 - 1.0           # hygrometer

# Switching and dimming
light1.switch(False)
light1.switch("on")

light2.dim(1.0) # full brightness
light2.dim(0.5) # dim halfway

# Utility functions
#   format_temperature: returns a temperature in a human-readable form, using units configured in Domoticz
#   format defaults to .1f, ie. one decimal
domoticz.format_temperature(22.0)           #   "22.0°C"
domoticz.format_temperature(101.235, ".2f") # "101.24°F"

# Example - Climate data
climate = domoticz.get_device("pool.climate_sensor")

print( "The temperature is {}, humidity is {:.0%} ", 
  domoticz.format_temperature(climate.temperature), 
  climate.humidity )

```
