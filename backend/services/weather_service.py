import requests
from typing import Optional, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch current weather data from OpenWeatherMap"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"]
            }
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def get_forecast(self, lat: float, lon: float, hours: int = 72) -> Optional[list]:
        """Fetch weather forecast data"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(hours // 3, 40)  # API returns data in 3-hour intervals
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data["list"]:
                forecasts.append({
                    "timestamp": item["dt"],
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "wind_speed": item["wind"]["speed"]
                })
            
            return forecasts
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return None
    
    def geocode_city(self, city: str) -> Optional[Dict]:
        """Get coordinates for a city name"""
        try:
            url = "http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": city,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    "city": data[0]["name"],
                    "country": data[0]["country"],
                    "lat": data[0]["lat"],
                    "lon": data[0]["lon"]
                }
            return None
        except Exception as e:
            logger.error(f"Error geocoding city: {e}")
            return None