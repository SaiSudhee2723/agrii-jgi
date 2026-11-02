import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.crop import CropRecommendationRequest, CropRecommendationResponse
from app.services.crop_service import CropRecommendationService
from app.core.security import get_current_user_optional
from app.core.supabase import get_supabase_client
from app.core.database import get_sqlite_conn

logger = logging.getLogger("geosense.api.crop")
router = APIRouter()

@router.post("/recommend", response_model=CropRecommendationResponse, summary="Get ML-driven crop recommendations")
async def recommend_crops(
    payload: CropRecommendationRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Module 2: Machine Learning Crop Recommendation.
    Accepts: Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, pH, Rainfall.
    Returns: Primary crop recommendation, calibrated confidence, alternative crops, and agro-advisories.
    Persists recommendation into database for authenticated user.
    """
    try:
        response = CropRecommendationService.recommend(payload)
    except Exception as e:
        logger.error(f"Crop recommendation failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating crop recommendations."
        )

    user_id = current_user.get("sub") if current_user else "anonymous"
    now_str = datetime.utcnow().isoformat() + "Z"
    rec_id = str(uuid.uuid4())

    # Persist to local database
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO crop_recommendations (
                id, user_id, input_nitrogen, input_phosphorus, input_potassium,
                input_temperature, input_humidity, input_ph, input_rainfall,
                primary_recommendation, confidence_score, alternative_crops,
                growing_conditions, farming_advice, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec_id, user_id, payload.nitrogen, payload.phosphorus, payload.potassium,
            payload.temperature, payload.humidity, payload.ph, payload.rainfall,
            response.primary_crop, response.confidence_score,
            json.dumps([c.model_dump() for c in response.alternative_crops]),
            json.dumps(response.growing_conditions.model_dump()),
            json.dumps(response.farming_recommendations),
            now_str
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not persist crop recommendation to local db: {e}")

    # Persist to Supabase if connected
    supabase = get_supabase_client()
    if supabase and user_id != "anonymous":
        try:
            record = {
                "id": rec_id,
                "user_id": user_id,
                "input_nitrogen": payload.nitrogen,
                "input_phosphorus": payload.phosphorus,
                "input_potassium": payload.potassium,
                "input_temperature": payload.temperature,
                "input_humidity": payload.humidity,
                "input_ph": payload.ph,
                "input_rainfall": payload.rainfall,
                "primary_recommendation": response.primary_crop,
                "confidence_score": response.confidence_score,
                "alternative_crops": [c.model_dump() for c in response.alternative_crops],
                "growing_conditions": response.growing_conditions.model_dump(),
                "farming_advice": response.farming_recommendations
            }
            supabase.table("crop_recommendations").insert(record).execute()
        except Exception as e:
            logger.warning(f"Could not persist crop recommendation to Supabase: {e}")

    return response

@router.get("/history", summary="Get saved crop recommendations for the authenticated user")
async def get_crop_history(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """Returns authentic crop recommendation history. Returns [] if none saved."""
    user_id = current_user.get("sub") if current_user else "anonymous"

    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM crop_recommendations
        WHERE user_id = ? OR user_id = 'anonymous'
        ORDER BY created_at DESC LIMIT 15
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        try:
            alternatives = json.loads(r["alternative_crops"]) if r["alternative_crops"] else []
        except Exception:
            alternatives = []
        try:
            advice = json.loads(r["farming_advice"]) if r["farming_advice"] else []
        except Exception:
            advice = []

        results.append({
            "id": r["id"],
            "primary_crop": r["primary_recommendation"],
            "confidence_score": r["confidence_score"],
            "input_n": r["input_nitrogen"],
            "input_p": r["input_phosphorus"],
            "input_k": r["input_potassium"],
            "input_ph": r["input_ph"],
            "input_rainfall": r["input_rainfall"],
            "input_temperature": r["input_temperature"],
            "alternatives": alternatives,
            "farming_advice": advice,
            "created_at": r["created_at"],
            "data_source": "Scikit-Learn Calibrated Random Forest Model"
        })

    return results
