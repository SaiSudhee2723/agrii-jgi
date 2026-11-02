from typing import List, Optional
from pydantic import BaseModel, Field

class CurrentWeather(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: Optional[float] = None
    weather_condition: str
    weather_icon: str
    precipitation_mm: float
    uv_index: Optional[float] = None

class ForecastDay(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation_sum: float
    precipitation_probability: int
    condition: str

class FarmingAlert(BaseModel):
    severity: str  # 'info', 'warning', 'critical'
    category: str  # 'frost', 'heat_stress', 'heavy_rain', 'drought_watch', 'pest_risk'
    title: str
    description: str
    advisory_action: str

class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    location_name: str
    current: CurrentWeather
    forecast: List[ForecastDay]
    alerts: List[FarmingAlert]
    source: str
    last_updated: str = ""
    is_available: bool = True


