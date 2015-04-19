## DomoticzControl
A simple library for interacting with Domoticz using its JSON API.

###Example usage
Note that this is an early draft; syntax will probably change, and hopefully for the better. :)

```python
# Creating the object...
domoticz = Domoticz(BASE_URI).authorize("username", "hunter2")

# Accessing devices...
light1 = domoticz.get_device("heater") # ... by name
light2 = domoticz.get_device(11)       # ... by ID   (idx)

# Switching stuff on and off
light1.switch(boolean)
light2.set_level(0.5) # dim halfway

# Climate data
pool      = domoticz.get_device("pool.thermometer")
pool_temp = pool.get_temperature()
print( "The pool temperature is " + domoticz.format_temperature(pool_temp) ) # using units as set up in Domoticz
# ... or with better control of the output format:
domoticz.format_temperature(pool_temp, ".2f") # two decimal places, default is 1
# ... also supports humidity
domoticz.get_device("somewhere.hygrometer").get_humidity() # returns 0.0 - 1.0

```
