# openweathermap api
import requests, json, datetime

# retrive config settings for URL
from owmconfig import *

# returns current weather dictionary 
def getcurrent():
    # request json and convert to python
    exclude = "minutely,hourly,daily"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat="+lat+"&lon="+lon+"&exclude="+exclude+"&units="+units+"&appid="+api_key
    response = requests.get(url) 
    x = response.json()
    c = x["current"]
    
    current = {
        "time": datetime.datetime.fromtimestamp(c["dt"]),
        "temp": c["temp"],
        "humidity": c["humidity"],
        "weather": c["weather"][0]["main"]
    }
    return current

# returns forecast dictionary (forecast_hr = 0 - coming hour)
def getforecast(forecast_hr):
    # request json and convert to python
    exclude = "current,minutely,daily"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat="+lat+"&lon="+lon+"&exclude="+exclude+"&units="+units+"&appid="+api_key
    response = requests.get(url) 
    x = response.json()
    hourly = x["hourly"]
    
    # 0 indicates current hour, so 1 is added
    f = hourly[forecast_hr+1]
    forecast = {
        "time": datetime.datetime.fromtimestamp(f["dt"]),
        "temp": f["temp"],
        "humidity": f["humidity"],
        "weather": f["weather"][0]["main"]
    }
    return forecast
