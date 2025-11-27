from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, AQIRecord
from models.schemas import AQIPredictionResponse
from ml.predict import AQIPredictor
from services.aqi_service import get_aqi_category, get_health_tips
from services.weather_service import WeatherService
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/aqi", tags=["AQI"])

predictor = AQIPredictor()
weather_service = WeatherService()

@router.get("/current/{city}")
async def get_current_aqi(city: str, db: Session = Depends(get_db)):
    """Get current AQI for a city"""
    try:
        # Get coordinates
        location = weather_service.geocode_city(city)
        if not location:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Get latest record from database
        recent_record = db.query(AQIRecord).filter(
            AQIRecord.city == location['city']
        ).order_by(AQIRecord.timestamp.desc()).first()
        
        if recent_record and (datetime.utcnow() - recent_record.timestamp).seconds < 3600:
            return {
                "city": recent_record.city,
                "country": recent_record.country,
                "aqi": recent_record.aqi,
                "category": get_aqi_category(recent_record.aqi),
                "pollutants": {
                    "pm25": recent_record.pm25,
                    "pm10": recent_record.pm10,
                    "o3": recent_record.o3,
                    "no2": recent_record.no2,
                    "so2": recent_record.so2,
                    "co": recent_record.co
                },
                "weather": {
                    "temperature": recent_record.temperature,
                    "humidity": recent_record.humidity,
                    "wind_speed": recent_record.wind_speed,
                    "pressure": recent_record.pressure
                },
                "timestamp": recent_record.timestamp.isoformat()
            }
        
        # Fallback to live API
        from services.aqi_service import AQIService
        aqi_service = AQIService()
        aqi_data = aqi_service.get_aqi_by_city(city)
        
        if not aqi_data:
            raise HTTPException(status_code=404, detail="AQI data not available")
        
        return {
            "city": aqi_data.get('city', city),
            "aqi": aqi_data.get('aqi'),
            "category": get_aqi_category(aqi_data.get('aqi')),
            "pollutants": {
                "pm25": aqi_data.get('pm25'),
                "pm10": aqi_data.get('pm10'),
                "o3": aqi_data.get('o3'),
                "no2": aqi_data.get('no2'),
                "so2": aqi_data.get('so2'),
                "co": aqi_data.get('co')
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current AQI: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/predict/{city}")
async def predict_aqi(
    city: str,
    hours: str = Query("24,48,72", description="Comma-separated prediction hours"),
    db: Session = Depends(get_db)
):
    """Predict future AQI for a city"""
    try:
        # Parse hours
        hour_list = [int(h.strip()) for h in hours.split(",")]
        
        # Get coordinates
        location = weather_service.geocode_city(city)
        if not location:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Get prediction
        prediction_result = predictor.predict_with_fallback(
            location['lat'],
            location['lon'],
            location['city'],
            hour_list
        )
        
        if not prediction_result:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
        current_aqi = prediction_result['current_aqi']
        
        return {
            "city": prediction_result['city'],
            "current_aqi": current_aqi,
            "aqi_category": get_aqi_category(current_aqi),
            "predictions": prediction_result['predictions'],
            "health_tips": get_health_tips(current_aqi),
            "generated_at": prediction_result['generated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting AQI: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@router.get("/historical/{city}")
async def get_historical_aqi(
    city: str,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get historical AQI data for a city"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        records = db.query(AQIRecord).filter(
            AQIRecord.city.ilike(f"%{city}%"),
            AQIRecord.timestamp >= cutoff_date
        ).order_by(AQIRecord.timestamp).all()
        
        if not records:
            raise HTTPException(status_code=404, detail="No historical data found")
        
        data = [{
            "timestamp": r.timestamp.isoformat(),
            "aqi": r.aqi,
            "pm25": r.pm25,
            "pm10": r.pm10,
            "temperature": r.temperature,
            "humidity": r.humidity
        } for r in records]
        
        return {
            "city": records[0].city,
            "country": records[0].country,
            "data": data,
            "count": len(data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/compare")
async def compare_cities(
    cities: str = Query(..., description="Comma-separated city names"),
    db: Session = Depends(get_db)
):
    """Compare current AQI across multiple cities"""
    try:
        city_list = [c.strip() for c in cities.split(",")]
        
        if len(city_list) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 cities allowed")
        
        results = []
        
        for city in city_list:
            location = weather_service.geocode_city(city)
            if not location:
                continue
            
            recent_record = db.query(AQIRecord).filter(
                AQIRecord.city == location['city']
            ).order_by(AQIRecord.timestamp.desc()).first()
            
            if recent_record:
                results.append({
                    "city": recent_record.city,
                    "country": recent_record.country,
                    "aqi": recent_record.aqi,
                    "category": get_aqi_category(recent_record.aqi),
                    "timestamp": recent_record.timestamp.isoformat()
                })
        
        return {
            "cities": results,
            "count": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing cities: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")