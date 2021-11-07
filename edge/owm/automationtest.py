import owmforecast

MOISTURE_MAX = 60
MOISTURE_MIN = 20
MOISTURE_CRIT_MIN = 5

TEMP_MAX = 28
TEMP_MIN = 4

# state - previous state of water
def water(moisture, temperature, state):
    
    # Continue watering
    if (state):
        if (moisture > MOISTURE_MAX):
            return "W0"
        else:
            return "W1"
    
    # Critical level that must be watered
    if (moisture < MOISTURE_CRIT_MIN):
        return "W1"
    
    # Determine if plant should be watered
    if (owmforecast.getnextrain()['hour'] < 3):
        # Will rain in the next three hours
        if not(owmforecast.getcurrent()['rain'] or owmforecast.getforecast(0)['rain']):
            # Will rain within an hour
            return "W1"
    else:
        # Not raining soonWithin acceptable temperature
        if (temperature < TEMP_MAX and temperature > TEMP_MIN):
            # Within acceptable temperature
            if (moisture < MOISTURE_MIN):
                # Soil is dry
                return "W1"
    
    return "W0"
            
test_data = [
    # [moisture, temperature, state]
    [  0,  0,  1],
    [100,  0,  1],
    [  0,  0,  0],
    [ 30,  3,  0],
    [ 30, 31,  0],
    [ 15, 25,  0],
    [ 50, 25,  0]
]

for d in test_data:
    print(f"M:{d[0]}, \tT:{d[1]}, \tS:{d[2]} = \t" + water(d[0], d[1], d[2]))

moisture = int(input("Moisture in %: "))
temperature = int(input("Temp in C: "))
state = int(input("Is the plant being watered? (1/0): "))
print(water(moisture, temperature, state))
    