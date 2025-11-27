import requests
from typing import Optional, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)

class AQIService:
    def __init__(self):
        self.waqi_key = settings.WAQI_API_KEY
        self.base_url = "https://api.waqi.info"
    
    def get_current_aqi(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch current AQI data from WAQI"""
        try:
            url = f"{self.base_url}/feed/geo:{lat};{lon}/"
            params = {"token": self.waqi_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "ok":
                result = {
                    "aqi": float(data["data"]["aqi"]),
                    "city": data["data"]["city"]["name"],
                }
                
                # Extract pollutant data
                iaqi = data["data"].get("iaqi", {})
                result.update({
                    "pm25": iaqi.get("pm25", {}).get("v"),
                    "pm10": iaqi.get("pm10", {}).get("v"),
                    "o3": iaqi.get("o3", {}).get("v"),
                    "no2": iaqi.get("no2", {}).get("v"),
                    "so2": iaqi.get("so2", {}).get("v"),
                    "co": iaqi.get("co", {}).get("v")
                })
                
                return result
            return None
        except Exception as e:
            logger.error(f"Error fetching AQI data: {e}")
            return None
    
    def get_aqi_by_city(self, city: str) -> Optional[Dict]:
        """Fetch AQI data by city name"""
        try:
            url = f"{self.base_url}/feed/{city}/"
            params = {"token": self.waqi_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "ok":
                result = {
                    "aqi": float(data["data"]["aqi"]),
                    "city": data["data"]["city"]["name"],
                    "lat": data["data"]["city"]["geo"][0],
                    "lon": data["data"]["city"]["geo"][1]
                }
                
                iaqi = data["data"].get("iaqi", {})
                result.update({
                    "pm25": iaqi.get("pm25", {}).get("v"),
                    "pm10": iaqi.get("pm10", {}).get("v"),
                    "o3": iaqi.get("o3", {}).get("v"),
                    "no2": iaqi.get("no2", {}).get("v"),
                    "so2": iaqi.get("so2", {}).get("v"),
                    "co": iaqi.get("co", {}).get("v")
                })
                
                return result
            return None
        except Exception as e:
            logger.error(f"Error fetching AQI by city: {e}")
            return None
    
    def search_cities(self, query: str) -> list:
        """Search for cities with AQI stations"""
        try:
            url = f"{self.base_url}/search/"
            params = {"token": self.waqi_key, "keyword": query}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "ok":
                return [
                    {
                        "city": station["station"]["name"],
                        "lat": station["station"]["geo"][0],
                        "lon": station["station"]["geo"][1]
                    }
                    for station in data["data"]
                ]
            return []
        except Exception as e:
            logger.error(f"Error searching cities: {e}")
            return []

def get_aqi_category(aqi: float) -> str:
    """Get AQI category and color"""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def get_health_tips(aqi: float) -> list:
    """Get health recommendations based on AQI"""
    if aqi <= 50:
        return [
            "Air quality is excellent. Perfect for outdoor activities!",
            "Enjoy your time outside with no restrictions.",
            "Great day for exercise and outdoor sports."
        ]
    elif aqi <= 100:
        return [
            "Air quality is acceptable for most people.",
            "Unusually sensitive individuals should consider limiting prolonged outdoor exertion.",
            "Good day for outdoor activities with minor precautions."
        ]
    elif aqi <= 150:
        return [
            "Sensitive groups should reduce prolonged outdoor exertion.",
            "Children and adults with respiratory issues should take breaks during outdoor activities.",
            "Consider wearing a mask if you're in a sensitive group."
        ]
    elif aqi <= 200:
        return [
            "Everyone should reduce prolonged outdoor exertion.",
            "Wear a mask when going outside.",
            "Keep windows closed and use air purifiers indoors.",
            "Reschedule outdoor activities if possible."
        ]
    elif aqi <= 300:
        return [
            "Avoid all outdoor physical activities.",
            "Everyone should wear N95 masks outdoors.",
            "Keep windows and doors closed.",
            "Use HEPA air purifiers indoors.",
            "Sensitive groups should remain indoors."
        ]
    else:
        return [
            "Health alert: Stay indoors and avoid all outdoor activities.",
            "Use N95 or higher-grade masks if you must go outside.",
            "Seal windows and doors. Use multiple air purifiers.",
            "Seek medical attention if you experience symptoms.",
            "Follow local emergency guidelines."
        ]