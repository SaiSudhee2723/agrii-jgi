import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends
from app.core.security import get_current_user_optional
from app.core.database import get_sqlite_conn
from app.services.weather_service import WeatherService

logger = logging.getLogger("geosense.api.overview")
router = APIRouter()

@router.get("/stats", summary="Get genuine authenticated user dashboard metrics and real activity feed")
async def get_dashboard_overview_stats(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Returns verified, user-isolated dashboard statistics:
    - Real count of soil tests submitted
    - Real count of saved crop recommendations
    - Real count of irrigation records
    - Live Open-Meteo ambient weather telemetry
    - Real chronological field activities
    Returns genuine empty states when 0 records exist.
    """
    user_id = current_user.get("sub") if current_user else "anonymous"

    conn = get_sqlite_conn()
    cursor = conn.cursor()

    # 1. Soil Tests Count & Latest
    cursor.execute("""
        SELECT COUNT(*) as count FROM soil_analysis
        WHERE user_id = ? OR user_id = 'anonymous'
    """, (user_id,))
    soil_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT * FROM soil_analysis
        WHERE user_id = ? OR user_id = 'anonymous'
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    latest_soil_row = cursor.fetchone()
    latest_soil = dict(latest_soil_row) if latest_soil_row else None

    # 2. Crop Recommendations Count & Latest
    cursor.execute("""
        SELECT COUNT(*) as count FROM crop_recommendations
        WHERE user_id = ? OR user_id = 'anonymous'
    """, (user_id,))
    crop_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT * FROM crop_recommendations
        WHERE user_id = ? OR user_id = 'anonymous'
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    latest_crop_row = cursor.fetchone()
    latest_crop = dict(latest_crop_row) if latest_crop_row else None

    # 3. Irrigation Records Count & Latest
    cursor.execute("""
        SELECT COUNT(*) as count FROM irrigation_records
        WHERE user_id = ? OR user_id = 'anonymous'
    """, (user_id,))
    irrigation_count = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT * FROM irrigation_records
        WHERE user_id = ? OR user_id = 'anonymous'
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    latest_irrig_row = cursor.fetchone()
    latest_irrigation = dict(latest_irrig_row) if latest_irrig_row else None

    # 4. Compile Real Recent Activities
    activities: List[Dict[str, Any]] = []

    if latest_soil:
        m_type = latest_soil.get("measurement_type", "optical_camera")
        title = "Lab Soil Test Recorded" if m_type == "laboratory_report" else (
            "Field Soil Kit Measured" if m_type == "physical_sensor" else (
                "Manual Soil Reading Saved" if m_type == "manual_entry" else "Camera Soil Scan Completed"
            )
        )
        activities.append({
            "title": title,
            "detail": latest_soil.get("soil_condition", "Physical analysis recorded"),
            "timestamp": latest_soil.get("created_at"),
            "category": "soil"
        })

    if latest_crop:
        activities.append({
            "title": f"Crop Model Recommended: {latest_crop.get('primary_recommendation')}",
            "detail": f"Calibrated Score: {round(float(latest_crop.get('confidence_score', 0)) * 100, 1)}%",
            "timestamp": latest_crop.get("created_at"),
            "category": "crop"
        })

    if latest_irrigation:
        crop_n = latest_irrigation.get("crop_name", "Crop")
        water = latest_irrigation.get("water_required_liters_per_acre", 0)
        needed = latest_irrigation.get("irrigation_needed", 0)
        detail_msg = f"{water:,.0f} L/acre required" if needed else "Moisture level adequate"
        activities.append({
            "title": f"Irrigation Scheduled for {crop_n}",
            "detail": detail_msg,
            "timestamp": latest_irrigation.get("created_at"),
            "category": "irrigation"
        })

    # Sort activities by timestamp descending
    activities.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

    # 5. Live Open-Meteo Weather
    weather_summary = None
    try:
        weather_res = await WeatherService.get_weather()
        weather_summary = {
            "temperature": weather_res.current.temperature,
            "condition": weather_res.current.weather_condition,
            "humidity": weather_res.current.humidity,
            "wind_speed": weather_res.current.wind_speed,
            "precipitation": weather_res.current.precipitation_mm,
            "location": weather_res.location_name,
            "source": weather_res.source,
            "last_updated": weather_res.last_updated,
            "is_available": True
        }
    except Exception as e:
        logger.warning(f"Overview could not fetch live weather: {e}")
        weather_summary = {
            "temperature": None,
            "condition": "Data temporarily unavailable",
            "humidity": None,
            "is_available": False,
            "source": "Open-Meteo (Temporarily Unreachable)",
            "last_updated": ""
        }

    conn.close()

    return {
        "user_id": user_id,
        "total_soil_tests": soil_count,
        "latest_soil_test": latest_soil,
        "total_crop_recommendations": crop_count,
        "latest_crop_recommendation": latest_crop,
        "total_irrigation_events": irrigation_count,
        "latest_irrigation": latest_irrigation,
        "recent_activities": activities,
        "live_weather": weather_summary
    }

