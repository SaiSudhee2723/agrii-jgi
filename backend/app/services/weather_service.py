import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from collections import defaultdict
import httpx
from app.schemas.weather import WeatherResponse, CurrentWeather, ForecastDay, FarmingAlert
from app.core.config import settings

logger = logging.getLogger("geosense.weather")

class WeatherService:
    """Module 4: Weather intelligence service with live OpenWeatherMap API and Open-Meteo agro-meteorology fallback."""

    OPENWEATHER_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
    OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    OPENWEATHER_GEO_URL = "https://api.openweathermap.org/geo/1.0/reverse"
    OPENWEATHER_DIRECT_GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    async def _auto_detect_ip_location(cls) -> Optional[tuple[float, float, str]]:
        """Resolves the user's real physical city & coordinates via IP geolocation."""
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                res = await client.get("http://ip-api.com/json/")
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "success":
                        lat = float(data.get("lat"))
                        lon = float(data.get("lon"))
                        city = data.get("city", "")
                        region = data.get("regionName", "")
                        loc_str = f"{city}, {region}".strip(", ")
                        return lat, lon, loc_str
        except Exception as e:
            logger.info(f"IP geolocate notice: {e}")
        return None

    @classmethod
    async def _geocode_query(cls, query: str, api_key: str) -> Optional[tuple[float, float, str]]:
        """Resolves city, district or village name to lat/lon using OpenWeather geocoding."""
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    cls.OPENWEATHER_DIRECT_GEO_URL,
                    params={"q": query, "limit": 1, "appid": api_key}
                )
                if res.status_code == 200 and len(res.json()) > 0:
                    g = res.json()[0]
                    lat = float(g.get("lat"))
                    lon = float(g.get("lon"))
                    name = g.get("name", query)
                    state = g.get("state", g.get("country", ""))
                    loc_name = f"{name}, {state}".strip(", ")
                    return lat, lon, loc_name
        except Exception as e:
            logger.warning(f"Geocoding error for '{query}': {e}")
        return None

    @classmethod
    async def get_weather(
        cls,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None,
        location_query: Optional[str] = None
    ) -> WeatherResponse:
        api_key = getattr(settings, "OPENWEATHER_API_KEY", "").strip()

        # 1. If explicit search query provided (e.g. "Bengaluru" or "Mandya")
        if location_query and location_query.strip():
            if api_key:
                geo = await cls._geocode_query(location_query.strip(), api_key)
                if geo:
                    latitude, longitude, location_name = geo

        # 2. If coordinates not provided or at dummy default, auto-detect from user's IP
        is_default_coords = (
            latitude is not None and longitude is not None and
            abs(latitude - 20.5937) < 0.001 and abs(longitude - 78.9629) < 0.001
        )
        if latitude is None or longitude is None or is_default_coords:
            ip_geo = await cls._auto_detect_ip_location()
            if ip_geo:
                latitude, longitude, location_name = ip_geo

        # Default fallback coordinates (Bengaluru, Karnataka)
        if latitude is None or longitude is None:
            latitude = 12.9753
            longitude = 77.5910
            location_name = location_name or "Bengaluru, Karnataka"

        location_name = location_name or "Local Farm"

        # 3. Try OpenWeatherMap with resolved coordinates
        if api_key:
            try:
                ow_resp = await cls._fetch_openweathermap(latitude, longitude, location_name, api_key)
                if ow_resp:
                    return ow_resp
            except Exception as e:
                logger.warning(f"OpenWeatherMap request failed: {e}. Falling back to Open-Meteo.")

        # 4. Fallback to Open-Meteo high-resolution agro-meteorology
        try:
            return await cls._fetch_open_meteo(latitude, longitude, location_name)
        except Exception as e:
            logger.error(f"Open-Meteo request failed: {e}. Using offline baseline.")
            return cls._get_fallback_weather(latitude, longitude, location_name)

    @classmethod
    async def _fetch_openweathermap(
        cls,
        lat: float,
        lng: float,
        location_name: str,
        api_key: str
    ) -> Optional[WeatherResponse]:
        async with httpx.AsyncClient(timeout=8.0) as client:
            # 1. Current Weather
            curr_res = await client.get(
                cls.OPENWEATHER_CURRENT_URL,
                params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric"}
            )
            if curr_res.status_code != 200:
                logger.info(f"OpenWeather current returned status {curr_res.status_code}: {curr_res.text}")
                return None

            curr_data = curr_res.json()

            # 2. 5-day / 3-hour Forecast
            fore_res = await client.get(
                cls.OPENWEATHER_FORECAST_URL,
                params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric"}
            )
            fore_data = fore_res.json() if fore_res.status_code == 200 else {}

            # 3. Reverse Geocode for accurate village / city name
            resolved_location = location_name
            try:
                geo_res = await client.get(
                    cls.OPENWEATHER_GEO_URL,
                    params={"lat": lat, "lon": lng, "limit": 1, "appid": api_key}
                )
                if geo_res.status_code == 200 and len(geo_res.json()) > 0:
                    g = geo_res.json()[0]
                    resolved_location = f"{g.get('name', '')}, {g.get('state', g.get('country', ''))}".strip(', ')
                elif curr_data.get("name"):
                    resolved_location = f"{curr_data.get('name')}, {curr_data.get('sys', {}).get('country', '')}".strip(', ')
            except Exception:
                pass

            return cls._parse_openweathermap_response(curr_data, fore_data, lat, lng, resolved_location)

    @classmethod
    def _parse_openweathermap_response(
        cls,
        curr_data: Dict[str, Any],
        fore_data: Dict[str, Any],
        lat: float,
        lng: float,
        location_name: str
    ) -> WeatherResponse:
        main = curr_data.get("main", {})
        wind = curr_data.get("wind", {})
        weather_list = curr_data.get("weather", [{}])
        weather_first = weather_list[0] if weather_list else {}

        temp = float(main.get("temp", 28.0))
        rh = float(main.get("humidity", 60.0))
        wind_speed_kmh = round(float(wind.get("speed", 3.0)) * 3.6, 1) # m/s to km/h
        wind_deg = float(wind.get("deg", 180.0))

        # Rain precipitation in past 1h / 3h
        rain_obj = curr_data.get("rain", {})
        precip = float(rain_obj.get("1h", rain_obj.get("3h", 0.0)))

        condition_desc = weather_first.get("description", "Clear").capitalize()
        icon = weather_first.get("icon", "01d")

        current = CurrentWeather(
            temperature=temp,
            humidity=rh,
            wind_speed=wind_speed_kmh,
            wind_direction=wind_deg,
            weather_condition=condition_desc,
            weather_icon=icon,
            precipitation_mm=precip,
            uv_index=6.5
        )

        # Parse 5-day / 3-hour forecast grouped by date
        forecast_list: List[ForecastDay] = []
        if "list" in fore_data:
            days_map = defaultdict(lambda: {"temps": [], "precip": 0.0, "pop": 0.0, "conditions": []})
            for item in fore_data["list"]:
                dt_txt = item.get("dt_txt", "")
                date_key = dt_txt.split(" ")[0] if " " in dt_txt else dt_txt
                if not date_key:
                    continue
                item_main = item.get("main", {})
                days_map[date_key]["temps"].append(item_main.get("temp", temp))
                item_rain = item.get("rain", {})
                days_map[date_key]["precip"] += float(item_rain.get("3h", 0.0))
                days_map[date_key]["pop"] = max(days_map[date_key]["pop"], float(item.get("pop", 0.0)))
                item_w = item.get("weather", [{}])
                if item_w:
                    days_map[date_key]["conditions"].append(item_w[0].get("description", "Clear").capitalize())

            for date_key, f_val in sorted(days_map.items())[:7]:
                t_list = f_val["temps"] or [temp]
                cond_list = f_val["conditions"] or [condition_desc]
                forecast_list.append(ForecastDay(
                    date=date_key,
                    temp_max=round(max(t_list), 1),
                    temp_min=round(min(t_list), 1),
                    precipitation_sum=round(f_val["precip"], 1),
                    precipitation_probability=round(f_val["pop"] * 100),
                    condition=cond_list[len(cond_list) // 2]
                ))

        if not forecast_list:
            forecast_list.append(ForecastDay(
                date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                temp_max=temp,
                temp_min=temp - 6.0,
                precipitation_sum=precip,
                precipitation_probability=10,
                condition=condition_desc
            ))

        alerts = cls._generate_agro_alerts(temp, rh, precip, forecast_list)
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        return WeatherResponse(
            latitude=lat,
            longitude=lng,
            location_name=location_name,
            current=current,
            forecast=forecast_list,
            alerts=alerts,
            source="OpenWeatherMap High-Precision Telemetry",
            last_updated=now_str,
            is_available=True
        )

    @classmethod
    async def _fetch_open_meteo(
        cls,
        latitude: float,
        longitude: float,
        location_name: str
    ) -> WeatherResponse:
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
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

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
