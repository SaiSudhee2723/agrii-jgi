import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.irrigation import IrrigationCalculationRequest, IrrigationCalculationResponse
from app.services.irrigation_service import IrrigationService
from app.core.security import get_current_user_optional
from app.core.supabase import get_supabase_client
from app.core.database import get_sqlite_conn

logger = logging.getLogger("geosense.api.irrigation")
router = APIRouter()

@router.post("/calculate", response_model=IrrigationCalculationResponse, summary="Compute water requirements & irrigation scheduling")
async def calculate_irrigation(
    payload: IrrigationCalculationRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Module 3: Software-based Smart Irrigation Calculations (FAO-56 Methodology).
    Calculates evapotranspiration rates, soil moisture deficit, weather-adjusted water demand,
    and precision irrigation schedules.
    Persists irrigation calculation record with authenticated user ID.
    """
    try:
        response = IrrigationService.calculate_irrigation(payload)
    except Exception as e:
        logger.error(f"Irrigation calculation failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error computing irrigation parameters."
        )

    user_id = current_user.get("sub") if current_user else "anonymous"
    now_str = datetime.utcnow().isoformat() + "Z"
    rec_id = str(uuid.uuid4())

    # Persist to local database
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO irrigation_records (
                id, user_id, crop_name, growth_stage, soil_moisture_percentage,
                field_area_acres, temperature_celsius, humidity_percentage,
                forecast_rainfall_mm, evapotranspiration_mm, water_required_liters_per_acre,
                total_water_liters, irrigation_needed, schedule_recommendation,
                water_saving_tips, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec_id, user_id, payload.crop_name, payload.growth_stage,
            payload.soil_moisture_percentage, payload.field_area_acres,
            payload.temperature_celsius or 28.0, payload.humidity_percentage or 55.0,
            payload.forecast_rainfall_mm or 0.0, response.evapotranspiration_rate_mm_day,
            response.water_required_liters_per_acre, response.total_water_liters,
            1 if response.irrigation_needed else 0, response.schedule_recommendation,
            json.dumps(response.water_saving_tips), now_str
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not persist irrigation record to local db: {e}")

    # Persist to Supabase if connected
    supabase = get_supabase_client()
    if supabase and user_id != "anonymous":
        try:
            record = {
                "id": rec_id,
                "user_id": user_id,
                "crop_name": payload.crop_name,
                "growth_stage": payload.growth_stage,
                "soil_moisture_percentage": payload.soil_moisture_percentage,
                "temperature_celsius": payload.temperature_celsius,
                "humidity_percentage": payload.humidity_percentage,
                "forecast_rainfall_mm": payload.forecast_rainfall_mm,
                "evapotranspiration_mm": response.evapotranspiration_rate_mm_day,
                "water_required_liters_per_acre": response.water_required_liters_per_acre,
                "irrigation_needed": response.irrigation_needed,
                "schedule_recommendation": response.schedule_recommendation,
                "water_saving_tips": response.water_saving_tips
            }
            supabase.table("irrigation_records").insert(record).execute()
        except Exception as e:
            logger.warning(f"Could not persist irrigation record to Supabase: {e}")

    return response

@router.get("/history", summary="Get genuine irrigation records for the authenticated user")
async def get_irrigation_history(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """Returns authentic irrigation calculation history. Returns [] if none recorded."""
    user_id = current_user.get("sub") if current_user else "anonymous"

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM irrigation_records
        WHERE user_id = ? OR user_id = 'anonymous'
        ORDER BY created_at DESC LIMIT 15
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        try:
            tips = json.loads(r["water_saving_tips"]) if r["water_saving_tips"] else []
        except Exception:
            tips = []

        results.append({
            "id": r["id"],
            "crop_name": r["crop_name"],
            "growth_stage": r["growth_stage"],
            "soil_moisture": r["soil_moisture_percentage"],
            "area_acres": r["field_area_acres"],
            "water_required_liters_per_acre": r["water_required_liters_per_acre"],
            "total_water_liters": r["total_water_liters"],
            "evapotranspiration_mm": r["evapotranspiration_mm"],
            "irrigation_needed": bool(r["irrigation_needed"]),
            "schedule_recommendation": r["schedule_recommendation"],
            "water_saving_tips": tips,
            "created_at": r["created_at"],
            "data_source": "FAO-56 Penman-Monteith Evapotranspiration Algorithm"
        })

    return results
