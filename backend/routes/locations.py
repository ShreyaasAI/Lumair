from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, Location
from services.weather_service import WeatherService
from services.aqi_service import AQIService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/locations", tags=["Locations"])

weather_service = WeatherService()
aqi_service = AQIService()

@router.get("/search")
async def search_locations(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """Search for cities with autocomplete"""
    try:
        # Search using geocoding API
        location = weather_service.geocode_city(q)
        
        if location:
            return {
                "results": [{
                    "city": location['city'],
                    "country": location['country'],
                    "lat": location['lat'],
                    "lon": location['lon'],
                    "display_name": f"{location['city']}, {location['country']}"
                }],
                "count": 1
            }
        
        return {"results": [], "count": 0}
        
    except Exception as e:
        logger.error(f"Error searching locations: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/popular")
async def get_popular_locations(db: Session = Depends(get_db)):
    """Get list of popular monitored cities"""
    try:
        locations = db.query(Location).filter(
            Location.is_active == 1
        ).limit(20).all()
        
        results = [{
            "city": loc.city,
            "country": loc.country,
            "lat": loc.lat,
            "lon": loc.lon,
            "display_name": f"{loc.city}, {loc.country}"
        } for loc in locations]
        
        return {
            "locations": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error fetching popular locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch locations")

@router.post("/add")
async def add_location(
    city: str,
    db: Session = Depends(get_db)
):
    """Add a new location to monitor"""
    try:
        # Geocode city
        location_data = weather_service.geocode_city(city)
        if not location_data:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Check if already exists
        existing = db.query(Location).filter(
            Location.city == location_data['city']
        ).first()
        
        if existing:
            return {
                "message": "Location already exists",
                "location": {
                    "city": existing.city,
                    "country": existing.country,
                    "lat": existing.lat,
                    "lon": existing.lon
                }
            }
        
        # Add new location
        new_location = Location(
            city=location_data['city'],
            country=location_data['country'],
            lat=location_data['lat'],
            lon=location_data['lon'],
            is_active=1
        )
        
        db.add(new_location)
        db.commit()
        db.refresh(new_location)
        
        return {
            "message": "Location added successfully",
            "location": {
                "city": new_location.city,
                "country": new_location.country,
                "lat": new_location.lat,
                "lon": new_location.lon
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding location: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add location")

@router.get("/nearby")
async def get_nearby_locations(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Find nearby monitored locations"""
    try:
        # Simple distance calculation (Haversine would be more accurate)
        from sqlalchemy import func
        
        # Approximate degree to km conversion
        lat_range = radius_km / 111.0  # 1 degree lat ≈ 111 km
        lon_range = radius_km / (111.0 * abs(func.cos(func.radians(lat))))
        
        locations = db.query(Location).filter(
            Location.is_active == 1,
            Location.lat.between(lat - lat_range, lat + lat_range),
            Location.lon.between(lon - lon_range, lon + lon_range)
        ).limit(20).all()
        
        results = [{
            "city": loc.city,
            "country": loc.country,
            "lat": loc.lat,
            "lon": loc.lon,
            "display_name": f"{loc.city}, {loc.country}"
        } for loc in locations]
        
        return {
            "locations": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error finding nearby locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to find locations")