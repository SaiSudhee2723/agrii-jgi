import logging
from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.weather import WeatherResponse
from app.services.weather_service import WeatherService

logger = logging.getLogger("geosense.api.weather")
router = APIRouter()

@router.get("/current", response_model=WeatherResponse, summary="Get weather data and agricultural alerts")
async def get_current_weather(
    lat: float = Query(20.5937, ge=-90.0, le=90.0, description="Farm Latitude"),
    lon: float = Query(78.9629, ge=-180.0, le=180.0, description="Farm Longitude"),
    location_name: str = Query("Regional Farm", description="Human-readable location label")
):
    """
    Module 4: Weather Intelligence & Agro-advisories.
    
    Returns real-time temperature, humidity, precipitation, 7-day forecast,
    and automatic farming alerts from genuine Open-Meteo telemetry.
    """
    try:
        return await WeatherService.get_weather(latitude=lat, longitude=lon, location_name=location_name)
    except Exception as e:
        logger.error(f"Weather error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather telemetry temporarily unavailable. External Open-Meteo connection could not be established."
        )

