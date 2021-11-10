# openweathermap api
import requests, json, datetime
import os
import dotenv

# retrive config settings for URL
dotenv.load_dotenv()
lat = os.getenv("LAT")
lon = os.getenv("LON")
api_key = os.getenv("OWM_API_KEY")

base_url = "http://api.openweathermap.org/data/2.5/onecall?"
units = "metric"

# returns current weather dictionary 
def getcurrent():
    # request json and convert to python
    exclude = "minutely,hourly,daily,alerts"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat="+lat+"&lon="+lon+"&exclude="+exclude+"&units="+units+"&appid="+api_key
    response = requests.get(url) 
    x = response.json()
    c = x["current"]
    
    current = {
        "time": datetime.datetime.fromtimestamp(c["dt"]),
        "temp": c["temp"],
        "humidity": c["humidity"],
        "clouds": c["clouds"],
        "weather": c["weather"][0]["main"],
        "rain": 1 if c["weather"][0]["main"] == "Rain" else 0
    }
    return current

# returns forecast dictionary (forecast_hr = 0 - coming hour)
def getforecast(forecast_hr):
    # request json and convert to python
    exclude = "current,minutely,daily,alerts"
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
        "clouds": f["clouds"],
        "weather": f["weather"][0]["main"],
        "rain": 1 if f["weather"][0]["main"] == "Rain" else 0
    }
    return forecast

def getnextrain():
    # request json and convert to python
    exclude = "current,minutely,daily,alerts"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat="+lat+"&lon="+lon+"&exclude="+exclude+"&units="+units+"&appid="+api_key
    response = requests.get(url) 
    x = response.json()
    hourly = x["hourly"]
    
    # 0 indicates current hour, so 1 is added
    hr = 1
    for hr in range(1,21):
        f = hourly[hr]
        if (f["weather"][0]["main"] == "Rain"):
            forecast = {
                "time": datetime.datetime.fromtimestamp(f["dt"]),
                "temp": f["temp"],
                "humidity": f["humidity"],
                "clouds": f["clouds"],
                "weather": f["weather"][0]["main"],
                "rain": 1 if f["weather"][0]["main"] == "Rain" else 0,
                "hour": hr
            }
            return forecast
    return 0