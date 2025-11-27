import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import AQIRecord, Location
from services.weather_service import WeatherService
from services.aqi_service import AQIService
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, db: Session):
        self.db = db
        self.weather_service = WeatherService()
        self.aqi_service = AQIService()
    
    def collect_and_store(self, city: str, lat: float, lon: float, country: str = None):
        """Collect current AQI and weather data and store in database"""
        try:
            # Fetch AQI data
            aqi_data = self.aqi_service.get_current_aqi(lat, lon)
            if not aqi_data:
                logger.warning(f"No AQI data for {city}")
                return False
            
            # Fetch weather data
            weather_data = self.weather_service.get_current_weather(lat, lon)
            if not weather_data:
                logger.warning(f"No weather data for {city}")
                weather_data = {}
            
            # Create record
            record = AQIRecord(
                city=city,
                country=country or "Unknown",
                lat=lat,
                lon=lon,
                aqi=aqi_data.get("aqi"),
                pm25=aqi_data.get("pm25"),
                pm10=aqi_data.get("pm10"),
                o3=aqi_data.get("o3"),
                no2=aqi_data.get("no2"),
                so2=aqi_data.get("so2"),
                co=aqi_data.get("co"),
                temperature=weather_data.get("temperature"),
                humidity=weather_data.get("humidity"),
                wind_speed=weather_data.get("wind_speed"),
                pressure=weather_data.get("pressure"),
                timestamp=datetime.utcnow()
            )
            
            self.db.add(record)
            self.db.commit()
            logger.info(f"Collected and stored data for {city}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting data for {city}: {e}")
            self.db.rollback()
            return False
    
    def collect_all_active_locations(self):
        """Collect data for all active locations in database"""
        locations = self.db.query(Location).filter(Location.is_active == 1).all()
        
        success_count = 0
        for location in locations:
            if self.collect_and_store(
                location.city, 
                location.lat, 
                location.lon, 
                location.country
            ):
                success_count += 1
        
        logger.info(f"Data collection complete: {success_count}/{len(locations)} successful")
        return success_count
    
    def get_training_data(self, city: str = None, days: int = 90) -> pd.DataFrame:
        """Retrieve historical data for model training"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(AQIRecord).filter(AQIRecord.timestamp >= cutoff_date)
        
        if city:
            query = query.filter(AQIRecord.city == city)
        
        records = query.order_by(AQIRecord.timestamp).all()
        
        data = [{
            "city": r.city,
            "aqi": r.aqi,
            "pm25": r.pm25,
            "pm10": r.pm10,
            "o3": r.o3,
            "no2": r.no2,
            "so2": r.so2,
            "co": r.co,
            "temperature": r.temperature,
            "humidity": r.humidity,
            "wind_speed": r.wind_speed,
            "pressure": r.pressure,
            "timestamp": r.timestamp,
            "hour": r.timestamp.hour,
            "day_of_week": r.timestamp.weekday(),
            "month": r.timestamp.month
        } for r in records]
        
        return pd.DataFrame(data)
    
    def initialize_default_locations(self):
        """Add default major cities to monitor"""
        default_cities = [
            {"city": "Mumbai", "country": "India", "lat": 19.0760, "lon": 72.8777},
            {"city": "Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090},
            {"city": "Beijing", "country": "China", "lat": 39.9042, "lon": 116.4074},
            {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278},
            {"city": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060},
            {"city": "Los Angeles", "country": "USA", "lat": 34.0522, "lon": -118.2437},
            {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503},
            {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522},
        ]
        
        for city_data in default_cities:
            existing = self.db.query(Location).filter(
                Location.city == city_data["city"]
            ).first()
            
            if not existing:
                location = Location(**city_data)
                self.db.add(location)
        
        try:
            self.db.commit()
            logger.info("Default locations initialized")
        except Exception as e:
            logger.error(f"Error initializing locations: {e}")
            self.db.rollback()