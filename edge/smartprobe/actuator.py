import random
from owm import owmforecast

# P - pest
# W - water
# 0 - off
# 1 - on

# Moisture values in percentage
MOISTURE_MAX = 60
MOISTURE_MIN = 20
MOISTURE_CRIT_MIN = 5

# Temperature values in Celcius
TEMP_MAX = 28
TEMP_MIN = 4

# state - previous state of water
def generate_sprinkler_output(moisture, temperature, state):
    
    # Convert raw moisture value into percentage
    moisture = ( 100 - ( (moisture/4095.00) * 100 ) )
    
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

def generate_sprayer_output(image):
    state = random.randrange(0, 3)

    if state == 0:
        return "P1"
    else:
        return "P0"
