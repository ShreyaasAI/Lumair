from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AQIData(BaseModel):
    city: str
    country: str
    lat: float
    lon: float
    aqi: float
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    o3: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AQIPredictionResponse(BaseModel):
    city: str
    current_aqi: float
    predictions: List[dict]
    health_tips: List[str]
    aqi_category: str
    
class LocationSearch(BaseModel):
    city: str
    country: Optional[str] = None
    
class HistoricalAQIResponse(BaseModel):
    city: str
    data: List[dict]
    
class HealthTip(BaseModel):
    category: str
    tips: List[str]