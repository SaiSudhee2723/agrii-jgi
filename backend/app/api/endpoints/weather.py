import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.weather import WeatherResponse
from app.services.weather_service import WeatherService

logger = logging.getLogger("geosense.api.weather")
router = APIRouter()

@router.get("/current", response_model=WeatherResponse, summary="Get weather data and agricultural alerts")
async def get_current_weather(
    lat: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Farm Latitude"),
    lon: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Farm Longitude"),
    q: Optional[str] = Query(None, description="City, district, or place name query"),
    location_name: Optional[str] = Query(None, description="Human-readable location label")
):
    """
    Module 4: Weather Intelligence & Agro-advisories.
    
    Returns real-time temperature, humidity, precipitation, multi-day forecast,
    and automatic farming alerts from live OpenWeatherMap with auto IP geocoding.
    """
    try:
        return await WeatherService.get_weather(
            latitude=lat,
            longitude=lon,
            location_name=location_name,
            location_query=q
        )
    except Exception as e:
        logger.error(f"Weather error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather telemetry temporarily unavailable."
        )
