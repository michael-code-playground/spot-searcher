import requests
import json
    
def get_location():
    response = requests.get('https://ipinfo.io/')
    data = response.json()
    loc = data['loc'].split(',')
    lat = float(loc[0])
    lng = float(loc[1])
    city = data.get('city')
    country = data.get('country')
    location = (lat, lng, city, country)
    
    return location