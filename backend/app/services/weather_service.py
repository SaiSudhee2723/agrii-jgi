import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from app.schemas.weather import WeatherResponse, CurrentWeather, ForecastDay, FarmingAlert
from app.core.config import settings

logger = logging.getLogger("geosense.weather")

class WeatherService:
    """Module 4: Weather intelligence service with live Open-Meteo API integration and agro-advisory alerts."""

    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    async def get_weather(
        cls,
        latitude: float = 20.5937,
        longitude: float = 78.9629,
        location_name: str = "Regional Farm"
    ) -> WeatherResponse:
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
                "timezone": "auto"
            }

            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(cls.OPEN_METEO_URL, params=params)
                if res.status_code == 200:
                    data = res.json()
                    return cls._parse_open_meteo_response(data, latitude, longitude, location_name)
                else:
                    logger.warning(f"Open-Meteo returned status {res.status_code}.")
                    raise ValueError(f"Weather provider returned HTTP {res.status_code}")
        except Exception as e:
            logger.error(f"Weather API request error: {e}")
            raise ValueError(f"Live weather data temporarily unavailable from Open-Meteo: {str(e)}")

    @classmethod
    def _parse_open_meteo_response(
        cls,
        data: Dict[str, Any],
        lat: float,
        lng: float,
        location_name: str
    ) -> WeatherResponse:
        current_data = data.get("current", {})
        temp = float(current_data.get("temperature_2m", 28.0))
        rh = float(current_data.get("relative_humidity_2m", 60.0))
        precip = float(current_data.get("precipitation", 0.0))
        wind = float(current_data.get("wind_speed_10m", 12.0))
        wcode = int(current_data.get("weather_code", 0))

        condition_desc, icon = cls._wmo_code_to_desc(wcode)

        current = CurrentWeather(
            temperature=temp,
            humidity=rh,
            wind_speed=wind,
            wind_direction=float(current_data.get("wind_direction_10m", 180)),
            weather_condition=condition_desc,
            weather_icon=icon,
            precipitation_mm=precip,
            uv_index=6.5
        )

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip_sums = daily.get("precipitation_sum", [])
        precip_probs = daily.get("precipitation_probability_max", [])
        wcodes = daily.get("weather_code", [])

        forecast_list: List[ForecastDay] = []
        for i in range(min(7, len(dates))):
            c_desc, _ = cls._wmo_code_to_desc(wcodes[i] if i < len(wcodes) else 0)
            forecast_list.append(ForecastDay(
                date=dates[i],
                temp_max=float(max_temps[i]) if i < len(max_temps) else 30.0,
                temp_min=float(min_temps[i]) if i < len(min_temps) else 20.0,
                precipitation_sum=float(precip_sums[i]) if i < len(precip_sums) else 0.0,
                precipitation_probability=int(precip_probs[i]) if i < len(precip_probs) and precip_probs[i] is not None else 10,
                condition=c_desc
            ))

        alerts = cls._generate_agro_alerts(temp, rh, precip, forecast_list)
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        return WeatherResponse(
            latitude=lat,
            longitude=lng,
            location_name=location_name,
            current=current,
            forecast=forecast_list,
            alerts=alerts,
            source="Open-Meteo High-Resolution Agro-Meteorology API",
            last_updated=now_str,
            is_available=True
        )

    @classmethod
    def _generate_agro_alerts(
        cls,
        temp: float,
        rh: float,
        precip: float,
        forecast: List[ForecastDay]
    ) -> List[FarmingAlert]:
        alerts: List[FarmingAlert] = []

        # High heat stress
        if temp >= 38.0:
            alerts.append(FarmingAlert(
                severity="critical",
                category="heat_stress",
                title="Extreme Heat Stress Alert",
                description=f"Current temperature {temp}°C exceeds optimal physiological thresholds.",
                advisory_action="Schedule light evening irrigation to cool micro-climate; shield young nursery seedlings with shade netting."
            ))

        # High fungal / pest risk
        if rh >= 78.0 and 22.0 <= temp <= 32.0:
            alerts.append(FarmingAlert(
                severity="warning",
                category="pest_risk",
                title="Elevated Foliar Disease & Pest Risk",
                description=f"Persistent high humidity ({rh}%) and warm weather facilitate spore germination for blight and rust.",
                advisory_action="Avoid overhead sprinkler wetting; scout crop undersides for early fungal spots or aphid colonies."
            ))

        # Heavy rainfall check in upcoming 48 hours
        upcoming_rain = sum(f.precipitation_sum for f in forecast[:2])
        if upcoming_rain >= 35.0:
            alerts.append(FarmingAlert(
                severity="warning",
                category="heavy_rain",
                title="Heavy Rainfall Warning",
                description=f"{upcoming_rain} mm expected over next 48 hours.",
                advisory_action="Clear field drainage channels to prevent waterlogging; postpone fertilizer and pesticide spraying."
            ))

        if not alerts:
            alerts.append(FarmingAlert(
                severity="info",
                category="favorable",
                title="Favorable Field Conditions",
                description="Weather parameters are within normal seasonal range for crop growth.",
                advisory_action="Proceed with scheduled weeding, intercultural operations, and standard farm management."
            ))

        return alerts

    @classmethod
    def _wmo_code_to_desc(cls, code: int) -> tuple[str, str]:
        if code == 0:
            return "Clear sky", "sunny"
        elif code in (1, 2, 3):
            return "Partly cloudy", "partly_cloudy"
        elif code in (45, 48):
            return "Fog / Misty", "fog"
        elif code in (51, 53, 55, 61, 63):
            return "Light to moderate rain", "rain"
        elif code in (65, 80, 81, 82):
            return "Heavy rain / Showers", "heavy_rain"
        elif code in (95, 96, 99):
            return "Thunderstorm", "thunderstorm"
        return "Overcast", "cloudy"

    @classmethod
    def _get_fallback_weather(cls, lat: float, lng: float, location_name: str) -> WeatherResponse:
        current = CurrentWeather(
            temperature=28.5,
            humidity=58.0,
            wind_speed=11.2,
            weather_condition="Partly cloudy",
            weather_icon="partly_cloudy",
            precipitation_mm=0.0,
            uv_index=6.0
        )
        forecast = [
            ForecastDay(date="2026-11-03", temp_max=31.0, temp_min=20.0, precipitation_sum=0.0, precipitation_probability=10, condition="Clear sky"),
            ForecastDay(date="2026-11-04", temp_max=31.5, temp_min=20.5, precipitation_sum=0.0, precipitation_probability=15, condition="Partly cloudy"),
            ForecastDay(date="2026-11-05", temp_max=30.0, temp_min=19.5, precipitation_sum=2.0, precipitation_probability=30, condition="Scattered showers"),
            ForecastDay(date="2026-11-06", temp_max=29.0, temp_min=19.0, precipitation_sum=5.0, precipitation_probability=45, condition="Light rain"),
            ForecastDay(date="2026-11-07", temp_max=30.5, temp_min=19.8, precipitation_sum=0.0, precipitation_probability=20, condition="Partly cloudy"),
            ForecastDay(date="2026-11-08", temp_max=31.0, temp_min=20.0, precipitation_sum=0.0, precipitation_probability=10, condition="Clear sky"),
            ForecastDay(date="2026-11-09", temp_max=32.0, temp_min=21.0, precipitation_sum=0.0, precipitation_probability=10, condition="Sunny")
        ]
        alerts = [
            FarmingAlert(
                severity="info",
                category="favorable",
                title="Stable Farm Weather",
                description="Weather parameters are within normal seasonal range for crop growth.",
                advisory_action="Ideal window for scheduled irrigation and field intercultural operations."
            )
        ]
        return WeatherResponse(
            latitude=lat,
            longitude=lng,
            location_name=location_name,
            current=current,
            forecast=forecast,
            alerts=alerts,
            source="Agro-Meteorology Baseline Model (Offline Resilience)"
        )

